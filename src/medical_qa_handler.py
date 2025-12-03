"""
의료 질문 처리 모듈 (타입 A)
Chroma 검색 → 근거 점수 평가 → 웹 검색 폴백 → LLM 답변
"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from chromadb.api.models.Collection import Collection


class MedicalQAHandler:
    """의료 질문 처리 핸들러"""
    
    def __init__(
        self,
        vectorstore: Any,
        llm_model: str = "gpt-4o-mini",
        score_threshold: float = 0.6,
        top_k: int = 5
    ):
        """
        Args:
            vectorstore: Chroma 벡터스토어
            llm_model: LLM 모델명
            score_threshold: 근거 충분도 판단 기준점
            top_k: 검색할 상위 문서 수
        """
        self.vectorstore = vectorstore
        self.llm = ChatOpenAI(model=llm_model, temperature=0.0)
        self.score_threshold = score_threshold
        self.top_k = top_k
        
        # 웹 검색 도구 초기화
        try:
            self.web_search = TavilySearchResults(
                max_results=3,
                include_answer=True
            )
        except:
            self.web_search = None
    
    def _search_internal_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        내부 Chroma에서 문서 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            검색 결과 리스트 [{'document': ..., 'metadata': ..., 'distance': ...}, ...]
        """
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=self.top_k
        )
        
        documents = []
        for doc, score in results:
            # Chroma의 거리 점수(distance)를 관련성 점수(0-1)로 변환
            # 거리가 작을수록 유사도가 높음
            relevance_score = 1 - score  # 거리를 관련성으로 변환
            
            documents.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'relevance_score': relevance_score,
                'distance': score
            })
        
        return documents
    
    def _evaluate_relevance(self, documents: List[Dict[str, Any]], query: str) -> Tuple[List[Dict], float]:
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
        
        # LLM을 사용한 세부 관련성 평가
        evaluation_prompt = f"""다음 질문과 문서들의 관련성을 평가하세요.

질문: {query}

문서들:
"""
        for i, doc in enumerate(documents, 1):
            evaluation_prompt += f"\n문서 {i} (초기점수: {doc['relevance_score']:.2f}):\n{doc['content'][:300]}...\n"
        
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
        
        response = self.llm.invoke([HumanMessage(content=evaluation_prompt)])
        
        try:
            result = json.loads(response.content)
            evaluations = result.get("evaluations", [])
            
            # 각 문서의 점수 업데이트
            for eval_item in evaluations:
                doc_index = eval_item.get("doc_index", 1) - 1
                if 0 <= doc_index < len(documents):
                    documents[doc_index]['relevance_score'] = eval_item.get("score", 0)
                    documents[doc_index]['evaluation_reason'] = eval_item.get("reason", "")
            
            # 평균 점수 계산
            avg_score = sum(d['relevance_score'] for d in documents) / len(documents)
            
        except json.JSONDecodeError:
            avg_score = sum(d['relevance_score'] for d in documents) / len(documents)
        
        return documents, avg_score
    
    def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        웹에서 추가 정보 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            웹 검색 결과
        """
        if not self.web_search:
            return []
        
        try:
            results = self.web_search.invoke(query)
            web_documents = []
            
            for result in results:
                web_documents.append({
                    'content': result.get('content', result.get('snippet', '')),
                    'source': result.get('source', 'Unknown'),
                    'title': result.get('title', 'No title'),
                    'relevance_score': 0.7,  # 웹 검색은 기본적으로 0.7 점수
                    'is_web_source': True
                })
            
            return web_documents
        
        except Exception as e:
            print(f"웹 검색 오류: {e}")
            return []
    
    def _generate_answer_with_rag(
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
            source_info = doc.get('metadata', {})
            
            if doc.get('is_web_source'):
                source_text = f"[웹 출처: {doc['source']}]"
            else:
                source_text = f"[내부 데이터 출처: {source_info.get('file_name', 'Unknown')}]"
            
            context += f"{i}. ({relevance:.1%} 관련성) {source_text}\n"
            context += f"내용: {doc['content'][:500]}\n\n"
        
        rag_prompt = f"""당신은 반려동물 의료 전문 QA 어시스턴트입니다.

질문: {query}

참고 정보:
{context}

위의 참고 정보를 기반으로 정확하고 신뢰할 수 있는 답변을 제공하세요.
- 명확하고 이해하기 쉬운 언어 사용
- 정보의 출처와 신뢰도 명시
- 필요시 추가 전문가 상담 권유"""
        
        response = self.llm.invoke([HumanMessage(content=rag_prompt)])
        return response.content
    
    def handle_medical_question(self, query: str) -> Dict[str, Any]:
        """
        의료 질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            
        Returns:
            처리 결과 딕셔너리
        """
        print(f"\n[의료 질문 처리] {query}")
        print("-" * 60)
        
        result = {
            'question': query,
            'question_type': 'A',
            'timestamp': datetime.now().isoformat(),
            'internal_search_results': [],
            'web_search_results': [],
            'relevance_score': 0.0,
            'used_web_search': False,
            'answer': '',
            'sources': []
        }
        
        # 1단계: 내부 문서 검색
        print("1단계: 내부 문서 검색 중...")
        internal_docs = self._search_internal_documents(query)
        result['internal_search_results'] = len(internal_docs)
        
        if not internal_docs:
            print("  → 내부 문서 없음, 웹 검색 진행")
            result['used_web_search'] = True
            web_docs = self._web_search(query)
            result['web_search_results'] = len(web_docs)
            
            if web_docs:
                result['answer'] = self._generate_answer_with_rag(
                    query,
                    web_docs,
                    use_web_source=True
                )
                result['sources'] = web_docs[:3]
        else:
            # 2단계: 근거 평가
            print("2단계: 근거 관련성 평가 중...")
            evaluated_docs, avg_score = self._evaluate_relevance(internal_docs, query)
            result['relevance_score'] = avg_score
            
            print(f"  → 평균 관련성 점수: {avg_score:.2f}")
            print(f"  → Threshold: {self.score_threshold:.2f}")
            
            # 3단계: Threshold 판단
            if avg_score >= self.score_threshold:
                print("  → 내부 문서 충분, 웹 검색 불필요")
                result['answer'] = self._generate_answer_with_rag(query, evaluated_docs)
                result['sources'] = evaluated_docs[:3]
            else:
                print("  → 내부 문서 부족, 웹 검색 진행")
                result['used_web_search'] = True
                web_docs = self._web_search(query)
                result['web_search_results'] = len(web_docs)
                
                # 내부 + 웹 문서 결합
                combined_docs = evaluated_docs + web_docs
                result['answer'] = self._generate_answer_with_rag(
                    query,
                    combined_docs,
                    use_web_source=True
                )
                result['sources'] = combined_docs[:3]
        
        # 답변 재평가 (선택사항)
        print("3단계: 답변 품질 평가 중...")
        
        return result

