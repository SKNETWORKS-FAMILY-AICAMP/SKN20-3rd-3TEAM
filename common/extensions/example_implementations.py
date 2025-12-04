"""
예시 구현 (Example Implementations)
==================================
팀원들이 참고할 수 있는 기본 구현 예시입니다.
이 파일을 복사하여 각자의 구현을 진행하세요.

각 팀원은 다음과 같이 자신의 고도화 영역에 맞게 수정합니다:
1. 클래스명 변경 (예: ExampleEmbedding → MyAdvancedEmbedding)
2. 로직 구현
3. 테스트 작성
4. __init__.py에 등록
"""

from typing import List, Dict, Any, Tuple, Optional
import logging
from abc import ABC, abstractmethod

from common.base import (
    BaseEmbedding,
    BaseVectorStore,
    BaseRetriever,
    BaseRAGPipeline,
    BaseLLMClient,
    BaseWebSearch,
    RetrievalResult,
)
from common.models import QueryRequest, QueryResponse, SourceInfo, Document
from common.config import PipelineConfig, ModelConfig
from common.utils import setup_logging

logger = logging.getLogger(__name__)


# ============ 예시 1: 임베딩 모델 구현 ============
class ExampleEmbedding(BaseEmbedding):
    """
    예시 임베딩 구현
    
    팀원이 이 파일을 복사하여 다음을 구현할 수 있습니다:
    - OpenAI Embeddings
    - HuggingFace Embeddings
    - 커스텀 임베딩 모델
    - 로컬 임베딩 모델
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small", dimension: int = 1536, **kwargs):
        super().__init__(model_name, dimension, **kwargs)
        # TODO: 실제 구현에서는 여기서 모델을 로드합니다
        logger.info(f"✅ 임베딩 모델 로드: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트 임베딩
        
        팀원 구현 사항:
        - API 호출 또는 모델 추론
        - 에러 처리
        - 캐싱 (선택)
        """
        try:
            # 실제 구현 예시:
            # response = openai.Embedding.create(
            #     input=text,
            #     model=self.model_name
            # )
            # return response['data'][0]['embedding']
            
            # 목업 구현
            import random
            logger.debug(f"임베딩: {text[:50]}...")
            return [random.random() for _ in range(self.dimension)]
        
        except Exception as e:
            logger.error(f"임베딩 오류: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """배치 임베딩 (병렬 처리)"""
        try:
            logger.info(f"배치 임베딩 시작: {len(texts)}개 텍스트")
            
            # 실제 구현에서는 배치 API 사용:
            # response = openai.Embedding.create(
            #     input=texts,
            #     model=self.model_name
            # )
            # return [item['embedding'] for item in response['data']]
            
            embeddings = [self.embed_text(text) for text in texts]
            logger.info(f"✅ 배치 임베딩 완료")
            return embeddings
        
        except Exception as e:
            logger.error(f"배치 임베딩 오류: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원"""
        return self.dimension


# ============ 예시 2: 벡터 저장소 구현 ============
class ExampleVectorStore(BaseVectorStore):
    """
    예시 벡터 저장소 구현
    
    팀원이 이 파일을 복사하여 다음을 구현할 수 있습니다:
    - Chroma
    - Pinecone
    - Weaviate
    - Milvus
    - 로컬 벡터 저장소
    """
    
    def __init__(self, embedding_model: BaseEmbedding, collection_name: str = "default", **kwargs):
        super().__init__(embedding_model, collection_name, **kwargs)
        self.documents: Dict[str, Dict[str, Any]] = {}  # 목업 저장소
        logger.info(f"✅ 벡터 저장소 초기화: {collection_name}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """문서 추가"""
        try:
            logger.info(f"📝 문서 추가: {len(documents)}개")
            
            added_ids = []
            for doc in documents:
                doc_id = doc.get('id', f"doc_{len(self.documents)}")
                
                # 임베딩 생성
                embedding = self.embedding_model.embed_text(doc['content'])
                
                # 저장
                self.documents[doc_id] = {
                    **doc,
                    'embedding': embedding,
                }
                added_ids.append(doc_id)
            
            logger.info(f"✅ {len(added_ids)}개 문서 추가됨")
            return added_ids
        
        except Exception as e:
            logger.error(f"문서 추가 오류: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """검색"""
        try:
            logger.info(f"🔍 검색: {query}")
            
            # 쿼리 임베딩
            query_embedding = self.embedding_model.embed_text(query)
            
            # 유사도 계산 (예시: 코사인 유사도)
            results = []
            for doc_id, doc in self.documents.items():
                # 목업: 랜덤 점수
                import random
                similarity = random.random()
                
                result = RetrievalResult(
                    document_id=doc_id,
                    content=doc['content'],
                    score=similarity,
                    metadata=doc.get('metadata', {}),
                    retrieval_mode='similarity',
                )
                results.append(result)
            
            # Top-K 정렬
            results = sorted(results, key=lambda x: x.score, reverse=True)[:top_k]
            logger.info(f"✅ 검색 완료: {len(results)}개 결과")
            
            return results
        
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            raise
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """문서 삭제"""
        try:
            for doc_id in doc_ids:
                if doc_id in self.documents:
                    del self.documents[doc_id]
            logger.info(f"✅ {len(doc_ids)}개 문서 삭제됨")
            return True
        except Exception as e:
            logger.error(f"삭제 오류: {e}")
            return False
    
    def clear(self) -> bool:
        """모든 문서 삭제"""
        try:
            self.documents.clear()
            logger.info("✅ 모든 문서 삭제됨")
            return True
        except Exception as e:
            logger.error(f"초기화 오류: {e}")
            return False


# ============ 예시 3: 검색기 구현 ============
class ExampleRetriever(BaseRetriever):
    """
    예시 검색기 구현
    
    팀원이 이 파일을 복사하여 다음을 구현할 수 있습니다:
    - MMR (Maximum Marginal Relevance)
    - BM25 검색
    - 하이브리드 검색
    - 필터링 기반 검색
    """
    
    def __init__(self, vector_store: BaseVectorStore, **kwargs):
        super().__init__(vector_store, **kwargs)
        logger.info("✅ 검색기 초기화")
    
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[RetrievalResult]:
        """
        검색 실행
        
        팀원 구현 사항:
        - 기본 검색 + 고도화 로직
        - 필터링
        - 재순위 지정
        """
        try:
            logger.info(f"🔎 검색 시작: top_k={top_k}")
            
            # Step 1: 기본 검색
            results = self.vector_store.search(query, top_k * 2)  # 여유있게 검색
            
            # Step 2: 재순위 지정 (팀원이 추가로 구현)
            # 예: MMR, diversity 고려 등
            
            # Step 3: Top-K 반환
            results = results[:top_k]
            
            logger.info(f"✅ 검색 완료: {len(results)}개 결과")
            return results
        
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            raise


# ============ 예시 4: LLM 클라이언트 구현 ============
class ExampleLLMClient(BaseLLMClient):
    """
    예시 LLM 클라이언트 구현
    
    팀원이 이 파일을 복사하여 다음을 구현할 수 있습니다:
    - OpenAI API
    - Anthropic Claude
    - Google PaLM
    - 로컬 LLM
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7, **kwargs):
        super().__init__(model_name, temperature, **kwargs)
        logger.info(f"✅ LLM 클라이언트 초기화: {model_name}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """텍스트 생성"""
        try:
            logger.info(f"🤖 LLM 호출: {prompt[:50]}...")
            
            # 실제 구현:
            # response = openai.ChatCompletion.create(
            #     model=self.model_name,
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=self.temperature,
            # )
            # return response['choices'][0]['message']['content']
            
            # 목업 응답
            return "이것은 예시 답변입니다."
        
        except Exception as e:
            logger.error(f"생성 오류: {e}")
            raise
    
    def grade(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """구조화된 판정"""
        try:
            logger.info(f"⚖️ 평가 호출")
            
            # 목업: yes/no 판정
            return {
                'is_relevant': True,
                'score': 0.8,
            }
        
        except Exception as e:
            logger.error(f"평가 오류: {e}")
            raise


# ============ 예시 5: 웹 검색 구현 ============
class ExampleWebSearch(BaseWebSearch):
    """
    예시 웹 검색 구현
    
    팀원이 이 파일을 복사하여 다음을 구현할 수 있습니다:
    - Tavily
    - Google Search
    - Bing Search
    - DuckDuckGo
    """
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        logger.info("✅ 웹 검색 초기화")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """웹 검색 실행"""
        try:
            logger.info(f"🌐 웹 검색: {query}")
            
            # 실제 구현:
            # from tavily import TavilyClient
            # client = TavilyClient(api_key=self.api_key)
            # results = client.search(query, max_results=num_results)
            
            # 목업 결과
            results = [
                {
                    'title': f'검색 결과 {i}',
                    'url': f'https://example.com/{i}',
                    'content': f'검색 결과 {i}의 콘텐츠',
                }
                for i in range(num_results)
            ]
            
            logger.info(f"✅ 웹 검색 완료: {len(results)}개 결과")
            return results
        
        except Exception as e:
            logger.error(f"웹 검색 오류: {e}")
            raise


# ============ 예시 6: 고도화된 파이프라인 구현 ============
class ExampleAdvancedPipeline(BaseRAGPipeline):
    """
    예시 고도화 파이프라인
    
    팀원이 SimpleRAGPipeline을 상속하여 다음을 구현할 수 있습니다:
    - CRAG 패턴 (웹 검색 추가)
    - Multi-hop 검색
    - 답변 품질 검사
    - 캐싱 최적화
    - 비용 최적화
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_web_search = kwargs.get('use_web_search', True)
        logger.info("✅ 고도화 파이프라인 초기화")
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        고도화된 처리 로직
        
        추가 기능:
        - 웹 검색 통합
        - 답변 품질 검사
        - 멀티홉 검색
        """
        try:
            # 기본 처리
            response = super().process(query, **kwargs)
            
            # 추가 고도화 로직
            if self.use_web_search and not response['success']:
                logger.info("🌐 웹 검색 폴백 시작")
                # 웹 검색으로 재처리
            
            return response
        
        except Exception as e:
            logger.error(f"파이프라인 오류: {e}")
            raise


# ============ 통합 테스트 예시 ============
def test_example_implementations():
    """
    예시 구현 테스트
    
    팀원들은 이와 유사하게 자신의 구현을 테스트할 수 있습니다.
    """
    
    # 로깅 설정
    setup_logging()
    
    print("\n" + "="*50)
    print("예시 구현 테스트")
    print("="*50)
    
    # 1. 임베딩 모델 테스트
    print("\n1️⃣ 임베딩 모델 테스트")
    embedding = ExampleEmbedding(model_name="text-embedding-3-small")
    result = embedding.embed_text("테스트 텍스트")
    print(f"✅ 임베딩 완료: 차원 = {len(result)}")
    
    # 2. 벡터 저장소 테스트
    print("\n2️⃣ 벡터 저장소 테스트")
    vector_store = ExampleVectorStore(embedding_model=embedding)
    docs = [
        {'id': 'doc1', 'content': '강아지 피부 질환', 'metadata': {}},
        {'id': 'doc2', 'content': '고양이 질병', 'metadata': {}},
    ]
    vector_store.add_documents(docs)
    results = vector_store.search("반려동물 질환", top_k=2)
    print(f"✅ 검색 완료: {len(results)}개 결과")
    
    # 3. 검색기 테스트
    print("\n3️⃣ 검색기 테스트")
    retriever = ExampleRetriever(vector_store=vector_store)
    results = retriever.retrieve("강아지 피부 문제", top_k=2)
    print(f"✅ 검색 완료: {len(results)}개 결과")
    
    # 4. LLM 클라이언트 테스트
    print("\n4️⃣ LLM 클라이언트 테스트")
    llm = ExampleLLMClient(model_name="gpt-4o-mini")
    answer = llm.generate("강아지 피부 질환은 뭐예요?")
    print(f"✅ 생성 완료: {answer[:50]}...")
    
    grade = llm.grade("이것은 질문인가?")
    print(f"✅ 평가 완료: {grade}")
    
    # 5. 웹 검색 테스트
    print("\n5️⃣ 웹 검색 테스트")
    web_search = ExampleWebSearch(api_key="dummy_key")
    search_results = web_search.search("강아지 피부 질환", num_results=3)
    print(f"✅ 웹 검색 완료: {len(search_results)}개 결과")
    
    print("\n" + "="*50)
    print("✅ 모든 테스트 통과!")
    print("="*50)


if __name__ == "__main__":
    test_example_implementations()


