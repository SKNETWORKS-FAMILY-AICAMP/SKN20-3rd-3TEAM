"""
RAG 시스템 패키지
책임분리(SoC) 기반으로 구성된 모듈식 RAG 시스템

주요 모듈:
- config: 전역 설정 및 환경 변수
- utils: 유틸리티 (로깅, 직렬화)
- core: 벡터스토어, 임베딩, 기본 검색
- retrievers: 내부 검색과 웹 검색
- llm: LLM 클라이언트
- classifiers: 질문 분류기
- handlers: 유형별 질문 처리 핸들러
- external: 외부 API (카카오맵 등)
- pipelines: 파이프라인 오케스트레이션
- data: 데이터 수집 및 청킹
"""

# Core 기능
from .core import (
    get_embedding_model,
    create_vectorstore,
    load_vectorstore,
    create_retriever,
    SimpleRetriever
)

# 분류기
from .classifiers import (
    QuestionClassifier,
    QuestionType
)

# 핸들러
from .handlers import (
    MedicalHandler,
    HospitalHandler,
    GeneralHandler
)

# 검색기
from .retrievers import (
    InternalSearcher,
    WebSearcher
)

# LLM
from .llm import (
    LLMClient,
    get_llm_client
)

# 파이프라인
from .pipelines import (
    RAGOrchestrator
)

# 데이터 처리
from .data import (
    ingest_data,
    chunk_documents_with_token_range
)

# 외부 API
from .external import (
    HospitalMapper
)

# 설정
from .config import (
    get_settings,
    Settings
)

__all__ = [
    # Core
    'get_embedding_model',
    'create_vectorstore',
    'load_vectorstore',
    'create_retriever',
    'SimpleRetriever',
    
    # Classifiers
    'QuestionClassifier',
    'QuestionType',
    
    # Handlers
    'MedicalHandler',
    'HospitalHandler',
    'GeneralHandler',
    
    # Retrievers
    'InternalSearcher',
    'WebSearcher',
    
    # LLM
    'LLMClient',
    'get_llm_client',
    
    # Pipelines
    'RAGOrchestrator',
    
    # Data
    'ingest_data',
    'chunk_documents_with_token_range',
    
    # External
    'HospitalMapper',
    
    # Config
    'get_settings',
    'Settings'
]
