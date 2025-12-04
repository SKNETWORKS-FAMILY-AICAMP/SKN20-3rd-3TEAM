"""
기본 인터페이스 및 추상 클래스
===========================
모든 팀원의 구현이 따를 수 있는 기본 계약(Contract)을 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ============ 상수 정의 ============
class DocumentType(Enum):
    """문서 타입"""
    INTERNAL = "internal"      # 내부 문서
    WEB = "web"               # 웹 검색 결과
    DATABASE = "database"     # 데이터베이스
    UNKNOWN = "unknown"       # 기타


class RetrievalMode(Enum):
    """검색 모드"""
    SIMILARITY = "similarity"  # 유사도 기반
    BM25 = "bm25"             # BM25 알고리즘
    HYBRID = "hybrid"         # 하이브리드
    SEMANTIC = "semantic"     # 의미론적


# ============ 데이터 클래스 ============
@dataclass
class EmbeddingResult:
    """임베딩 결과"""
    text: str
    embedding: List[float]
    dimension: int
    model: str
    
    
@dataclass
class RetrievalResult:
    """검색 결과"""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    retrieval_mode: RetrievalMode


# ============ 추상 클래스 ============
class BaseEmbedding(ABC):
    """
    임베딩 모델의 기본 인터페이스
    
    팀원들은 다양한 임베딩 모델을 구현할 수 있습니다:
    - OpenAI Embeddings
    - HuggingFace Embeddings
    - Cohere Embeddings
    - 커스텀 임베딩
    """
    
    def __init__(self, model_name: str, dimension: Optional[int] = None, **kwargs):
        """
        Args:
            model_name: 모델 이름
            dimension: 임베딩 차원
        """
        self.model_name = model_name
        self.dimension = dimension or 1536  # 기본값: OpenAI 차원
        self.kwargs = kwargs
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (float 리스트)
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        배치 텍스트를 임베딩
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        pass


class BaseVectorStore(ABC):
    """
    벡터 저장소의 기본 인터페이스
    
    팀원들은 다양한 벡터 저장소를 구현할 수 있습니다:
    - Chroma
    - Pinecone
    - Weaviate
    - Milvus
    - 로컬 벡터 저장소
    """
    
    def __init__(self, embedding_model: BaseEmbedding, collection_name: str = "default", **kwargs):
        """
        Args:
            embedding_model: 임베딩 모델 인스턴스
            collection_name: 컬렉션 이름
        """
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.kwargs = kwargs
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        문서를 벡터 저장소에 추가
        
        Args:
            documents: 문서 리스트 (id, content, metadata 포함)
            
        Returns:
            추가된 문서 ID 리스트
        """
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        쿼리로 유사 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            
        Returns:
            검색 결과 리스트
        """
        pass
    
    @abstractmethod
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        문서 삭제
        
        Args:
            doc_ids: 삭제할 문서 ID 리스트
            
        Returns:
            성공 여부
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        모든 문서 삭제
        
        Returns:
            성공 여부
        """
        pass


class BaseRetriever(ABC):
    """
    문서 검색기의 기본 인터페이스
    
    팀원들은 다양한 검색 전략을 구현할 수 있습니다:
    - Top-K 유사도 검색
    - MMR (Maximum Marginal Relevance)
    - BM25 검색
    - 필터링 기반 검색
    - 하이브리드 검색
    """
    
    def __init__(self, vector_store: BaseVectorStore, **kwargs):
        """
        Args:
            vector_store: 벡터 저장소 인스턴스
        """
        self.vector_store = vector_store
        self.kwargs = kwargs
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[RetrievalResult]:
        """
        쿼리로 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            **kwargs: 추가 검색 옵션
            
        Returns:
            검색 결과 리스트
        """
        pass
    
    def set_top_k(self, top_k: int):
        """Top-K 값 설정"""
        self.top_k = top_k


class BaseRAGPipeline(ABC):
    """
    RAG 파이프라인의 기본 인터페이스
    
    팀원들은 다양한 RAG 패턴을 구현할 수 있습니다:
    - 단순 RAG
    - CRAG (Corrective RAG)
    - Multi-hop RAG
    - Agent-based RAG
    - 비용 최적화 RAG
    """
    
    def __init__(self, 
                 retriever: BaseRetriever,
                 embedding_model: BaseEmbedding,
                 vector_store: BaseVectorStore,
                 llm_model: str = "gpt-4o-mini",
                 **kwargs):
        """
        Args:
            retriever: 검색기 인스턴스
            embedding_model: 임베딩 모델 인스턴스
            vector_store: 벡터 저장소 인스턴스
            llm_model: LLM 모델 이름
        """
        self.retriever = retriever
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.llm_model = llm_model
        self.kwargs = kwargs
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Step 1: 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            
        Returns:
            검색 결과 리스트
        """
        pass
    
    @abstractmethod
    def grade(self, query: str, documents: List[RetrievalResult]) -> Tuple[List[bool], Dict[str, Any]]:
        """
        Step 2: 문서 관련성 평가
        
        Args:
            query: 원본 쿼리
            documents: 검색된 문서 리스트
            
        Returns:
            (관련성 판정 리스트, 평가 상세 정보)
        """
        pass
    
    @abstractmethod
    def generate(self, query: str, documents: List[RetrievalResult]) -> str:
        """
        Step 3: 답변 생성
        
        Args:
            query: 사용자 질문
            documents: 관련 문서 리스트
            
        Returns:
            생성된 답변 텍스트
        """
        pass
    
    @abstractmethod
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        전체 RAG 파이프라인 실행
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 옵션
            
        Returns:
            {
                'question': str,
                'answer': str,
                'sources': List[Dict],
                'metadata': Dict
            }
        """
        pass


class BaseLLMClient(ABC):
    """
    LLM 클라이언트의 기본 인터페이스
    
    팀원들은 다양한 LLM을 연동할 수 있습니다:
    - OpenAI API
    - Anthropic Claude
    - Google PaLM
    - 로컬 LLM (Ollama, LLaMA)
    """
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """
        Args:
            model_name: 모델 이름
            temperature: 창의성 수준 (0~1)
            max_tokens: 최대 토큰 수
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 프롬프트
            **kwargs: 추가 옵션
            
        Returns:
            생성된 텍스트
        """
        pass
    
    @abstractmethod
    def grade(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        구조화된 판정 (yes/no 등)
        
        Args:
            prompt: 프롬프트
            **kwargs: 추가 옵션
            
        Returns:
            판정 결과
        """
        pass


class BaseWebSearch(ABC):
    """
    웹 검색 도구의 기본 인터페이스
    
    팀원들은 다양한 웹 검색을 구현할 수 있습니다:
    - Tavily
    - Google Search
    - Bing Search
    - DuckDuckGo
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Args:
            api_key: API 키
        """
        self.api_key = api_key
        self.kwargs = kwargs
    
    @abstractmethod
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        웹 검색 실행
        
        Args:
            query: 검색 쿼리
            num_results: 반환할 결과 개수
            
        Returns:
            검색 결과 리스트 (title, url, content 포함)
        """
        pass


