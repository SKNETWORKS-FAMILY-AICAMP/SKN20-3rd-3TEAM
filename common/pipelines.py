"""
기본 RAG 파이프라인 구현
======================
공통 기준이 되는 단순 RAG 파이프라인
팀원들이 이를 상속하여 고도화할 수 있습니다.
"""

from typing import List, Dict, Any, Tuple, Optional
import time
import logging
from datetime import datetime

from .base import (
    BaseRAGPipeline,
    BaseRetriever,
    BaseEmbedding,
    BaseVectorStore,
    BaseLLMClient,
)
from .models import (
    QueryRequest,
    QueryResponse,
    SourceInfo,
    RetrievalResult,
    Document,
    ChatMessage,
    ChatHistory,
)
from .config import PipelineConfig, Constants

logger = logging.getLogger(__name__)


class SimpleRAGPipeline(BaseRAGPipeline):
    """
    단순 RAG 파이프라인 (공통 기준)
    
    처리 흐름:
    1. Retrieve: 쿼리와 유사한 문서 검색
    2. Grade: 검색된 문서의 관련성 평가 (선택사항)
    3. Generate: 관련 문서를 컨텍스트로 답변 생성
    4. Return: 답변 + 출처 반환
    
    팀원들이 상속하여 다음을 고도화할 수 있습니다:
    - 더 복잡한 그레이딩 로직
    - 웹 검색 추가
    - 멀티홉 검색
    - 답변 품질 검사
    """
    
    def __init__(self,
                 retriever: BaseRetriever,
                 embedding_model: BaseEmbedding,
                 vector_store: BaseVectorStore,
                 llm_client: BaseLLMClient,
                 config: Optional[PipelineConfig] = None,
                 **kwargs):
        """
        Args:
            retriever: 검색기
            embedding_model: 임베딩 모델
            vector_store: 벡터 저장소
            llm_client: LLM 클라이언트
            config: 파이프라인 설정
        """
        super().__init__(retriever, embedding_model, vector_store, llm_client.model_name, **kwargs)
        self.llm_client = llm_client
        self.config = config or PipelineConfig()
        self.chat_history: Optional[ChatHistory] = None
        self.metrics = {
            'retrieval_time': 0,
            'grading_time': 0,
            'generation_time': 0,
            'total_time': 0,
        }
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievalResult]:
        """
        Step 1: 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            
        Returns:
            검색 결과 리스트
        """
        start_time = time.time()
        
        if top_k is None:
            top_k = self.config.top_k
        
        try:
            logger.info(f"🔍 검색 시작: query='{query}', top_k={top_k}")
            
            # 벡터 저장소에서 검색
            results = self.vector_store.search(query, top_k)
            
            self.metrics['retrieval_time'] = time.time() - start_time
            logger.info(f"✅ 검색 완료: {len(results)}개 문서 검색됨 ({self.metrics['retrieval_time']:.2f}초)")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ 검색 오류: {e}")
            raise
    
    def grade(self, query: str, documents: List[RetrievalResult]) -> Tuple[List[bool], Dict[str, Any]]:
        """
        Step 2: 문서 관련성 평가
        
        Args:
            query: 원본 쿼리
            documents: 검색된 문서 리스트
            
        Returns:
            (관련성 판정 리스트, 평가 상세 정보)
        """
        start_time = time.time()
        
        if not self.config.grade_documents or not documents:
            return [True] * len(documents), {}
        
        try:
            logger.info(f"🔎 문서 등급 평가 시작: {len(documents)}개 문서")
            
            relevance_scores = []
            grade_results = []
            
            for i, doc in enumerate(documents):
                # LLM으로 관련성 평가
                grade_result = self.llm_client.grade(
                    prompt=self._get_grade_prompt(query, doc.content)
                )
                
                # 판정 결과 추출
                is_relevant = grade_result.get('is_relevant', True)
                relevance_score = grade_result.get('score', 0.5)
                
                relevance_scores.append(relevance_score)
                grade_results.append(is_relevant)
                
                logger.debug(f"  [{i+1}/{len(documents)}] 관련성: {relevance_score:.2f}, 판정: {'YES' if is_relevant else 'NO'}")
            
            self.metrics['grading_time'] = time.time() - start_time
            
            # 관련 문서 개수 확인
            relevant_count = sum(grade_results)
            logger.info(f"✅ 평가 완료: {relevant_count}/{len(documents)}개 문서가 관련됨 ({self.metrics['grading_time']:.2f}초)")
            
            return grade_results, {
                'relevant_count': relevant_count,
                'total_count': len(documents),
                'relevance_scores': relevance_scores,
            }
        
        except Exception as e:
            logger.error(f"❌ 평가 오류: {e}")
            # 오류 발생 시 모든 문서를 관련있는 것으로 처리
            return [True] * len(documents), {'error': str(e)}
    
    def generate(self, query: str, documents: List[RetrievalResult], context: Optional[str] = None) -> str:
        """
        Step 3: 답변 생성
        
        Args:
            query: 사용자 질문
            documents: 관련 문서 리스트
            context: 추가 컨텍스트 (선택사항)
            
        Returns:
            생성된 답변
        """
        start_time = time.time()
        
        try:
            logger.info(f"🤖 답변 생성 시작: {len(documents)}개 문서 기반")
            
            # 컨텍스트 구성
            if context is None:
                context = self._build_context(documents)
            
            # 프롬프트 구성
            prompt = self._get_generation_prompt(query, context)
            
            # LLM으로 답변 생성
            answer = self.llm_client.generate(prompt)
            
            self.metrics['generation_time'] = time.time() - start_time
            logger.info(f"✅ 답변 생성 완료 ({self.metrics['generation_time']:.2f}초)")
            
            return answer
        
        except Exception as e:
            logger.error(f"❌ 생성 오류: {e}")
            raise
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        전체 RAG 파이프라인 실행
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 옵션
                - top_k: 검색할 문서 개수
                - temperature: LLM 창의성
                - include_sources: 출처 포함 여부
                
        Returns:
            {
                'query': str,           # 원본 질문
                'answer': str,          # 생성된 답변
                'sources': List,        # 참고 출처
                'metrics': Dict,        # 성능 메트릭
                'success': bool,        # 성공 여부
            }
        """
        start_time = time.time()
        self.metrics = {'retrieval_time': 0, 'grading_time': 0, 'generation_time': 0, 'total_time': 0}
        
        try:
            logger.info(f"🚀 RAG 파이프라인 시작: '{query}'")
            
            # Step 1: 문서 검색
            top_k = kwargs.get('top_k', self.config.top_k)
            documents = self.retrieve(query, top_k)
            
            if not documents:
                logger.warning("⚠️ 검색된 문서 없음")
                return self._error_response(query, "검색된 관련 문서가 없습니다")
            
            # Step 2: 문서 관련성 평가
            grade_results, grade_info = self.grade(query, documents)
            
            # 관련 문서만 필터링
            relevant_documents = [
                doc for doc, is_relevant in zip(documents, grade_results)
                if is_relevant
            ]
            
            # 최소 관련 문서 개수 확인
            if len(relevant_documents) < self.config.min_relevant_docs:
                logger.warning(f"⚠️ 관련 문서 부족: {len(relevant_documents)}/{self.config.min_relevant_docs}")
                # 여기서 웹 검색 등 추가 동작 가능
            
            # Step 3: 답변 생성
            answer = self.generate(query, relevant_documents)
            
            # Step 4: 출처 정보 생성
            sources = self._extract_sources(relevant_documents, grade_info.get('relevance_scores', []))
            
            self.metrics['total_time'] = time.time() - start_time
            
            logger.info(f"✅ 파이프라인 완료 ({self.metrics['total_time']:.2f}초)")
            
            # 응답 구성
            response = QueryResponse(
                query=query,
                answer=answer,
                sources=sources,
                response_time=self.metrics['total_time'],
                retrieval_time=self.metrics['retrieval_time'],
                generation_time=self.metrics['generation_time'],
                debug_info=grade_info,
            )
            
            return {
                'query': query,
                'answer': answer,
                'sources': [s.to_dict() for s in sources],
                'metrics': {
                    'retrieval_time': f"{self.metrics['retrieval_time']:.2f}s",
                    'grading_time': f"{self.metrics['grading_time']:.2f}s",
                    'generation_time': f"{self.metrics['generation_time']:.2f}s",
                    'total_time': f"{self.metrics['total_time']:.2f}s",
                },
                'debug_info': grade_info,
                'success': True,
            }
        
        except Exception as e:
            logger.error(f"❌ 파이프라인 오류: {e}")
            return self._error_response(query, str(e))
    
    # ========== 헬퍼 메서드 ==========
    
    def _build_context(self, documents: List[RetrievalResult]) -> str:
        """컨텍스트 구성"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[출처 {i}]\n{doc.content}\n")
        return "\n".join(context_parts)
    
    def _get_grade_prompt(self, query: str, document: str) -> str:
        """평가 프롬프트 생성"""
        return f"""다음 질문과 문서의 관련성을 평가하세요.

질문: {query}

문서:
{document[:500]}...

관련성이 있으면 'yes', 없으면 'no'를 한 단어로만 답변하세요."""
    
    def _get_generation_prompt(self, query: str, context: str) -> str:
        """생성 프롬프트 생성"""
        return f"""{Constants.SYSTEM_PROMPT}

다음 문맥을 기반으로 사용자의 질문에 답변하세요.

<문맥>
{context}
</문맥>

사용자 질문: {query}

답변:"""
    
    def _extract_sources(self, documents: List[RetrievalResult], relevance_scores: List[float]) -> List[SourceInfo]:
        """출처 정보 추출"""
        sources = []
        for i, doc in enumerate(documents[:self.config.top_k]):
            relevance_score = relevance_scores[i] if i < len(relevance_scores) else None
            
            source = SourceInfo(
                title=doc.metadata.get('title', f'문서 {i+1}'),
                document_id=doc.document_id,
                similarity_score=doc.score,
                relevance_score=relevance_score,
                metadata=doc.metadata,
            )
            sources.append(source)
        
        return sources
    
    def _error_response(self, query: str, error_message: str) -> Dict[str, Any]:
        """에러 응답 생성"""
        self.metrics['total_time'] = time.time() - time.time()
        return {
            'query': query,
            'answer': f"죄송합니다. 답변을 생성할 수 없습니다: {error_message}",
            'sources': [],
            'metrics': {'total_time': '0.00s'},
            'debug_info': {'error': error_message},
            'success': False,
        }
    
    def set_chat_history(self, chat_history: ChatHistory):
        """대화 기록 설정"""
        self.chat_history = chat_history
    
    def get_metrics(self) -> Dict[str, float]:
        """파이프라인 메트릭 반환"""
        return self.metrics


# ========== 사용 예시 ==========
"""
from common.base import BaseRetriever, BaseVectorStore, BaseEmbedding, BaseLLMClient
from common.pipelines import SimpleRAGPipeline
from common.config import PipelineConfig

# 각 컴포넌트 초기화 (팀원별로 구현)
retriever = MyRetriever(vector_store)
embedding = MyEmbedding(model_name="text-embedding-3-small")
vector_store = MyVectorStore(embedding)
llm_client = MyLLMClient(model_name="gpt-4o-mini")

# 파이프라인 생성
pipeline = SimpleRAGPipeline(
    retriever=retriever,
    embedding_model=embedding,
    vector_store=vector_store,
    llm_client=llm_client,
    config=PipelineConfig()
)

# 처리
response = pipeline.process("강아지 피부 질환의 증상은?")
print(response['answer'])
print(response['sources'])

# 고도화 예시 - CRAG 패턴 구현
class CRAGPipeline(SimpleRAGPipeline):
    def process(self, query: str, **kwargs):
        # 웹 검색 로직 추가
        # 멀티홉 검색 추가
        # 답변 품질 검사 추가
        return super().process(query, **kwargs)
"""


