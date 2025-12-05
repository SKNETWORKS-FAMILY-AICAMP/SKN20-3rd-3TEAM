"""
의료 질문 처리 핸들러 (타입 A)
Chroma 검색 → 근거 점수 평가 → 웹 검색 폴백 → LLM 답변
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseHandler
from src.llm import get_llm_client
from src.retrievers import InternalSearcher, WebSearcher
from src.utils import get_logger

logger = get_logger(__name__)


class MedicalHandler(BaseHandler):
    """의료 질문 처리 핸들러"""
    
    def __init__(
        self,
        vectorstore: Any,
        internal_searcher: Optional[InternalSearcher] = None,
        web_searcher: Optional[WebSearcher] = None,
        llm_model: str = "gpt-4o-mini",
        score_threshold: float = 0.6,
        top_k: int = 5
    ):
        """
        Args:
            vectorstore: Chroma 벡터스토어
            internal_searcher: 내부 검색기 (기본값: 새로 생성)
            web_searcher: 웹 검색기 (기본값: 새로 생성)
            llm_model: LLM 모델명
            score_threshold: 근거 충분도 판단 기준점
            top_k: 검색할 상위 문서 수
        """
        self.vectorstore = vectorstore
        self.llm = get_llm_client(model=llm_model, temperature=0.0)
        self.score_threshold = score_threshold
        self.top_k = top_k
        
        # 검색기 초기화
        self.internal_searcher = internal_searcher or InternalSearcher(vectorstore, top_k=top_k)
        self.web_searcher = web_searcher or WebSearcher()
        
        logger.info(f"MedicalHandler 초기화: threshold={score_threshold}, top_k={top_k}")
    
    def _evaluate_relevance(
        self,
        documents: List[Dict[str, Any]],
        query: str
    ) -> tuple[List[Dict[str, Any]], float]:
        """
        문서의 관련성 평가 및 평균 점수 계산
        
        Args:
            documents: 검색된 문서 리스트
            query: 원본 질문
            
        Returns:
            (평가된 문서 리스트, 평균 관련성 점수)
        """
        if not documents:
            return [], 0.0
        
        logger.debug(f"관련성 평가 시작: {len(documents)}개 문서")
        
        # LLM을 사용한 세부 관련성 평가
        evaluation_prompt = f"""다음 질문과 문서들의 관련성을 평가하세요.

질문: {query}

문서들:
"""
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')[:300]
            relevance = doc.get('relevance_score', 0)
            evaluation_prompt += f"\n문서 {i} (초기점수: {relevance:.2f}):\n{content}...\n"
        
        evaluation_prompt += f"""
각 문서에 대해 다음을 고려하여 관련성을 0-1 사이의 값으로 평가하세요:
1. 질문에 직접적인 답변 제공 여부
2. 정보의 신뢰도 및 정확성
3. 현재성 및 적용 가능성

응답 형식:
{{
    "evaluations": [
        {{"doc_index": 1, "score": 0.9, "reason": "..."}},
        {{"doc_index": 2, "score": 0.5, "reason": "..."}}
    ],
    "overall_confidence": 0.7
}}"""
        
        try:
            response = self.llm.invoke(evaluation_prompt)
            result = self.llm.parse_json(response)
            
            evaluations = result.get("evaluations", [])
            
            # 각 문서의 점수 업데이트
            for eval_item in evaluations:
                doc_index = eval_item.get("doc_index", 1) - 1
                if 0 <= doc_index < len(documents):
                    documents[doc_index]['relevance_score'] = eval_item.get("score", 0)
                    documents[doc_index]['evaluation_reason'] = eval_item.get("reason", "")
            
            # 평균 점수 계산
            avg_score = sum(d.get('relevance_score', 0) for d in documents) / len(documents)
            
            logger.debug(f"평가 완료: 평균 점수 {avg_score:.2f}")
        
        except Exception as e:
            logger.error(f"LLM 평가 실패: {str(e)}")
            avg_score = sum(d.get('relevance_score', 0) for d in documents) / len(documents)
        
        return documents, avg_score
    
    def _generate_answer(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        use_web_source: bool = False
    ) -> str:
        """
        RAG 기반 답변 생성
        
        Args:
            query: 질문
            documents: 참고 문서 리스트
            use_web_source: 웹 소스 포함 여부
            
        Returns:
            생성된 답변
        """
        # 문서 컨텍스트 구성
        context = "다음은 신뢰할 수 있는 출처에서 제공된 정보입니다:\n\n"
        
        for i, doc in enumerate(documents[:3], 1):  # 상위 3개 문서만 사용
            relevance = doc.get('relevance_score', 0)
            metadata = doc.get('metadata', {})
            
            if doc.get('is_web_source'):
                source_text = f"[웹 출처: {doc.get('source', 'Unknown')}]"
            else:
                source_text = f"[내부 데이터 출처: {metadata.get('file_name', 'Unknown')}]"
            
            content = doc.get('content', '')[:500]
            context += f"{i}. ({relevance:.1%} 관련성) {source_text}\n"
            context += f"내용: {content}\n\n"
        
        rag_prompt = f"""당신은 반려동물 의료 전문 QA 어시스턴트입니다.

질문: {query}

참고 정보:
{context}

위의 참고 정보를 기반으로 정확하고 신뢰할 수 있는 답변을 제공하세요.
- 명확하고 이해하기 쉬운 언어 사용
- 정보의 출처와 신뢰도 명시
- 필요시 추가 전문가 상담 권유"""
        
        logger.debug("답변 생성 중...")
        try:
            response = self.llm.invoke(rag_prompt)
            return response
        except Exception as e:
            logger.error(f"답변 생성 실패: {str(e)}")
            return "죄송하지만 답변을 생성하는 중 오류가 발생했습니다."
    
    def handle(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        의료 질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터
            
        Returns:
            처리 결과 딕셔너리
        """
        logger.info(f"의료 질문 처리 시작: {query[:50]}...")
        
        result = {
            'question': query,
            'question_type': 'A',
            'timestamp': datetime.now().isoformat(),
            'internal_search_results': 0,
            'web_search_results': 0,
            'relevance_score': 0.0,
            'used_web_search': False,
            'answer': '',
            'sources': []
        }
        
        # 1단계: 내부 문서 검색
        logger.info("1단계: 내부 문서 검색")
        internal_docs = self.internal_searcher.search(query, top_k=self.top_k)
        result['internal_search_results'] = len(internal_docs)
        
        if not internal_docs:
            logger.info("내부 문서 없음, 웹 검색 진행")
            result['used_web_search'] = True
            web_docs = self.web_searcher.search(query)
            result['web_search_results'] = len(web_docs)
            
            if web_docs:
                result['answer'] = self._generate_answer(query, web_docs, use_web_source=True)
                result['sources'] = web_docs[:3]
            else:
                result['answer'] = "죄송하지만, 해당 질문에 대한 정보를 찾을 수 없습니다."
        else:
            # 2단계: 근거 평가
            logger.info("2단계: 근거 관련성 평가")
            evaluated_docs, avg_score = self._evaluate_relevance(internal_docs, query)
            result['relevance_score'] = avg_score
            
            logger.debug(f"평균 관련성 점수: {avg_score:.2f}, 임계값: {self.score_threshold:.2f}")
            
            # 3단계: 임계값 판단
            if avg_score >= self.score_threshold:
                logger.info("내부 문서 충분, 답변 생성")
                result['answer'] = self._generate_answer(query, evaluated_docs)
                result['sources'] = evaluated_docs[:3]
            else:
                logger.info("내부 문서 부족, 웹 검색 진행")
                result['used_web_search'] = True
                web_docs = self.web_searcher.search(query)
                result['web_search_results'] = len(web_docs)
                
                # 내부 + 웹 문서 결합
                combined_docs = evaluated_docs + web_docs
                result['answer'] = self._generate_answer(query, combined_docs, use_web_source=True)
                result['sources'] = combined_docs[:3]
        
        logger.info(f"의료 질문 처리 완료: 신뢰도 {result['relevance_score']:.2f}")
        return result

