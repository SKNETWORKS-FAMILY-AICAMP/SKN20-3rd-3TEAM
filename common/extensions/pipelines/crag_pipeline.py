"""
CRAG (Corrective RAG) 파이프라인 구현
===================================
기존 RAG에 웹 검색 폴백과 답변 품질 검사를 추가한 고도화 버전
"""

from typing import Dict, List, Any, Optional, Tuple
import time
import logging

from common.base import (
    BaseRAGPipeline,
    BaseRetriever,
    BaseEmbedding,
    BaseVectorStore,
    BaseLLMClient,
    BaseWebSearch,
    RetrievalResult,
)
from common.models import QueryResponse, SourceInfo
from common.config import PipelineConfig
from common.pipelines import SimpleRAGPipeline

logger = logging.getLogger(__name__)


class CRAGPipeline(SimpleRAGPipeline):
    """
    CRAG (Corrective RAG) 파이프라인
    
    기본 RAG에 다음 기능을 추가:
    1. 문서 관련성 평가 (Grade)
    2. 관련 문서 부족 시 웹 검색 폴백 (Web Search)
    3. 쿼리 재작성 (Query Rewrite)
    4. 답변 품질 검사 (Answer Grading)
    
    처리 흐름:
    질문 → Retrieve → Grade → 
    ├─ (관련 문서 있음) → Generate → Return
    └─ (관련 문서 없음) → Rewrite → WebSearch → Generate → Return
    """
    
    def __init__(self,
                 retriever: BaseRetriever,
                 embedding_model: BaseEmbedding,
                 vector_store: BaseVectorStore,
                 llm_client: BaseLLMClient,
                 web_search_client: Optional[BaseWebSearch] = None,
                 config: Optional[PipelineConfig] = None,
                 **kwargs):
        """
        Args:
            retriever: 검색기
            embedding_model: 임베딩 모델
            vector_store: 벡터 저장소
            llm_client: LLM 클라이언트
            web_search_client: 웹 검색 클라이언트 (선택사항)
            config: 파이프라인 설정
        """
        super().__init__(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=vector_store,
            llm_client=llm_client,
            config=config,
            **kwargs
        )
        
        self.web_search_client = web_search_client
        self.max_rewrite_attempts = config.max_rewrite_attempts if config else 3
        
        logger.info("✅ CRAG 파이프라인 초기화 완료")
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        CRAG 파이프라인 전체 처리
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 옵션
        
        Returns:
            처리 결과
        """
        start_time = time.time()
        self.metrics = {
            'retrieval_time': 0,
            'grading_time': 0,
            'web_search_time': 0,
            'generation_time': 0,
            'total_time': 0,
        }
        
        try:
            logger.info(f"🚀 CRAG 파이프라인 시작: '{query}'")
            
            # Step 1: 문서 검색
            top_k = kwargs.get('top_k', self.config.top_k)
            documents = self.retrieve(query, top_k)
            
            if not documents:
                logger.warning("⚠️ 검색된 문서 없음")
                return self._error_response(query, "검색된 문서가 없습니다")
            
            # Step 2: 문서 관련성 평가
            grade_results, grade_info = self.grade(query, documents)
            
            # 관련 문서 필터링
            relevant_documents = [
                doc for doc, is_relevant in zip(documents, grade_results)
                if is_relevant
            ]
            
            relevant_count = len(relevant_documents)
            logger.info(f"📊 관련성 평가: {relevant_count}/{len(documents)} 관련")
            
            # Step 3: 관련 문서 있는지 확인
            if relevant_count >= self.config.min_relevant_docs:
                # 관련 문서 충분 → 답변 생성
                logger.info("✅ 관련 문서 충분: 직접 답변 생성")
                answer = self.generate(query, relevant_documents)
                sources = self._extract_sources(relevant_documents, 
                                               grade_info.get('relevance_scores', []))
            
            else:
                # 관련 문서 부족 → 웹 검색
                logger.warning("❌ 관련 문서 부족: 웹 검색 시작")
                
                if not self.web_search_client:
                    logger.error("⚠️ 웹 검색 클라이언트 없음")
                    return self._error_response(
                        query,
                        "내부 문서가 부족하고 웹 검색 기능이 비활성화됨"
                    )
                
                # Step 3-1: 쿼리 재작성
                rewritten_query = self._rewrite_query(query)
                logger.info(f"📝 쿼리 재작성: '{rewritten_query}'")
                
                # Step 3-2: 웹 검색
                web_results = self._web_search(rewritten_query)
                
                if not web_results:
                    logger.warning("⚠️ 웹 검색 결과 없음")
                    answer = self.generate(query, relevant_documents)
                    sources = self._extract_sources(relevant_documents, [])
                else:
                    # 웹 검색 결과로 답변 생성
                    logger.info(f"🌐 웹 검색 {len(web_results)}개 결과 획득")
                    answer = self._generate_with_web_search(query, web_results)
                    sources = self._extract_web_sources(web_results)
            
            # Step 4: 답변 품질 검사
            answer_quality, quality_reason = self._grade_answer(query, answer)
            
            if not answer_quality and relevant_count < len(documents):
                # 품질이 낮고 시도 가능하면 재시도
                logger.warning(f"⚠️ 답변 품질 낮음: {quality_reason}")
                # 여기서 재시도 로직 추가 가능
            
            self.metrics['total_time'] = time.time() - start_time
            
            logger.info(f"✅ CRAG 파이프라인 완료 ({self.metrics['total_time']:.2f}초)")
            
            # 응답 구성
            return {
                'query': query,
                'answer': answer,
                'sources': [s.to_dict() for s in sources],
                'metrics': {
                    'retrieval_time': f"{self.metrics['retrieval_time']:.2f}s",
                    'grading_time': f"{self.metrics['grading_time']:.2f}s",
                    'web_search_time': f"{self.metrics['web_search_time']:.2f}s",
                    'generation_time': f"{self.metrics['generation_time']:.2f}s",
                    'total_time': f"{self.metrics['total_time']:.2f}s",
                },
                'debug_info': {
                    'relevant_count': relevant_count,
                    'total_count': len(documents),
                    'web_search_used': len(relevant_documents) < self.config.min_relevant_docs,
                    'answer_quality': answer_quality,
                    'quality_reason': quality_reason,
                    **grade_info,
                },
                'success': True,
            }
        
        except Exception as e:
            logger.error(f"❌ CRAG 파이프라인 오류: {e}")
            return self._error_response(query, str(e))
    
    def _rewrite_query(self, query: str, attempt: int = 1) -> str:
        """
        쿼리 재작성
        
        내부 문서가 부족할 때 웹 검색에 적합하도록 쿼리를 재작성합니다.
        
        Args:
            query: 원본 쿼리
            attempt: 재작성 시도 횟수
        
        Returns:
            재작성된 쿼리
        """
        try:
            if attempt > self.max_rewrite_attempts:
                logger.warning(f"⚠️ 최대 재작성 시도 횟수 도달 ({self.max_rewrite_attempts})")
                return query
            
            logger.info(f"📝 쿼리 재작성 시도 {attempt}/{self.max_rewrite_attempts}")
            
            prompt = f"""사용자의 질문을 웹 검색에 더 적합하도록 재작성하세요.
원본 질문: {query}

요구사항:
1. 더 구체적이고 명확하게
2. 검색 엔진이 이해하기 쉽게
3. 핵심 키워드를 강조
4. 한 문장으로 유지

재작성된 질문:"""
            
            rewritten = self.llm_client.generate(prompt)
            
            logger.info(f"✅ 재작성 완료: {rewritten}")
            
            return rewritten.strip()
        
        except Exception as e:
            logger.error(f"❌ 쿼리 재작성 오류: {e}")
            return query
    
    def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        웹 검색 실행
        
        Args:
            query: 검색 쿼리
        
        Returns:
            웹 검색 결과 리스트
        """
        try:
            start_time = time.time()
            
            logger.info(f"🌐 웹 검색 시작: '{query}'")
            
            num_results = self.config.web_search_results
            results = self.web_search_client.search(query, num_results=num_results)
            
            self.metrics['web_search_time'] = time.time() - start_time
            
            logger.info(f"✅ 웹 검색 완료: {len(results)}개 결과 ({self.metrics['web_search_time']:.2f}초)")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ 웹 검색 오류: {e}")
            return []
    
    def _generate_with_web_search(self, query: str, web_results: List[Dict[str, Any]]) -> str:
        """
        웹 검색 결과를 포함한 답변 생성
        
        Args:
            query: 사용자 질문
            web_results: 웹 검색 결과
        
        Returns:
            생성된 답변
        """
        try:
            start_time = time.time()
            
            # 웹 결과를 컨텍스트로 변환
            context_parts = []
            for i, result in enumerate(web_results[:5], 1):  # 상위 5개만
                context_parts.append(f"[출처 {i}: {result.get('title', 'Unknown')}]\n{result.get('content', '')}\n")
            
            context = "\n".join(context_parts)
            
            # 프롬프트 생성
            prompt = f"""다음 웹 검색 결과를 기반으로 사용자의 질문에 답변하세요.
항상 출처를 명시하세요.

<웹 검색 결과>
{context}
</웹 검색 결과>

사용자 질문: {query}

답변:"""
            
            # 답변 생성
            answer = self.llm_client.generate(prompt)
            
            self.metrics['generation_time'] = time.time() - start_time
            
            logger.info(f"✅ 웹 기반 답변 생성 완료 ({self.metrics['generation_time']:.2f}초)")
            
            return answer
        
        except Exception as e:
            logger.error(f"❌ 웹 기반 생성 오류: {e}")
            raise
    
    def _grade_answer(self, query: str, answer: str) -> Tuple[bool, str]:
        """
        답변 품질 평가
        
        Args:
            query: 질문
            answer: 답변
        
        Returns:
            (품질 양호 여부, 평가 사유)
        """
        try:
            logger.info("⚖️ 답변 품질 평가 시작")
            
            if not self.config.check_answer_quality:
                return True, "품질 검사 비활성화"
            
            prompt = f"""다음 질문과 답변의 품질을 평가하세요.

질문: {query}

답변: {answer}

평가 기준:
- 질문에 직접 답변했는가?
- 정보가 정확한가?
- 출처가 명시되어 있는가?

'yes'로 양호, 'no'로 불량 판정하세요. (한 단어만)"""
            
            result = self.llm_client.grade(prompt)
            
            is_good = result.get('is_relevant', True)
            reason = "답변이 양호합니다" if is_good else "답변 품질이 낮을 수 있습니다"
            
            logger.info(f"⚖️ 평가 완료: {reason}")
            
            return is_good, reason
        
        except Exception as e:
            logger.error(f"❌ 품질 평가 오류: {e}")
            return True, "평가 실패 (기본값: 양호)"
    
    def _extract_web_sources(self, web_results: List[Dict[str, Any]]) -> List[SourceInfo]:
        """
        웹 검색 결과를 출처 정보로 변환
        
        Args:
            web_results: 웹 검색 결과
        
        Returns:
            출처 정보 리스트
        """
        sources = []
        
        for i, result in enumerate(web_results[:self.config.top_k]):
            source = SourceInfo(
                title=result.get('title', f'웹 결과 {i+1}'),
                url=result.get('url', ''),
                metadata={
                    'source': 'web_search',
                    'content': result.get('content', '')[:200] + '...',
                }
            )
            sources.append(source)
        
        return sources
    
    def _error_response(self, query: str, error_message: str) -> Dict[str, Any]:
        """에러 응답 생성"""
        return {
            'query': query,
            'answer': f"죄송합니다. 답변을 생성할 수 없습니다: {error_message}",
            'sources': [],
            'metrics': {
                'total_time': '0.00s',
            },
            'debug_info': {'error': error_message},
            'success': False,
        }

