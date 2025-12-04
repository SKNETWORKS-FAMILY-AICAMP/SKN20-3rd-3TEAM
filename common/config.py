"""
공통 설정 및 상수
================
프로젝트 전체에서 사용할 설정, 상수, 환경 변수를 정의합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()


# ============ 환경 설정 ============
class Environment(Enum):
    """실행 환경"""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


# ============ 로깅 레벨 ============
class LogLevel(Enum):
    """로깅 레벨"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ============ 데이터 설정 ============
@dataclass
class DataConfig:
    """데이터 관련 설정"""
    # 기본 데이터 경로
    data_dir: str = field(default="./data")
    raw_data_dir: str = field(default="./data/raw")
    processed_data_dir: str = field(default="./data/processed")
    
    # 문서 청킹
    chunk_size: int = field(default=1024)          # 청크 크기 (토큰)
    chunk_overlap: int = field(default=256)        # 청크 겹침
    
    # 벡터 저장소
    vector_store_dir: str = field(default="./chroma_db")
    collection_name: str = field(default="documents")
    
    # 캐시
    use_cache: bool = field(default=True)
    cache_dir: str = field(default="./cache")


# ============ 모델 설정 ============
@dataclass
class ModelConfig:
    """모델 관련 설정"""
    
    # ========== 임베딩 모델 ==========
    embedding_model: str = field(default="text-embedding-3-small")
    embedding_dimension: int = field(default=1536)
    embedding_batch_size: int = field(default=100)
    
    # ========== LLM 모델 ==========
    llm_model: str = field(default="gpt-4o-mini")
    llm_temperature: float = field(default=0.7)
    llm_max_tokens: Optional[int] = field(default=2048)
    llm_top_p: float = field(default=0.95)
    
    # ========== 평가 모델 ==========
    grader_model: str = field(default="gpt-4o-mini")
    grader_temperature: float = field(default=0.0)  # 일관성 중심
    
    # ========== 쿼리 재작성 모델 ==========
    rewriter_model: str = field(default="gpt-4o-mini")
    rewriter_temperature: float = field(default=0.7)
    
    # ========== API 키 ==========
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다")
        return True


# ============ 파이프라인 설정 ============
@dataclass
class PipelineConfig:
    """RAG 파이프라인 설정"""
    
    # ========== 검색 설정 ==========
    top_k: int = field(default=5)                   # 검색할 상위 문서 수
    retrieval_mode: str = field(default="similarity")  # similarity, bm25, hybrid
    min_similarity_score: float = field(default=0.5)   # 최소 유사도 점수
    
    # ========== 등급 평가 설정 ==========
    grade_documents: bool = field(default=True)    # 문서 등급 평가 여부
    relevance_threshold: float = field(default=0.5)    # 관련성 임계값 (0~1)
    min_relevant_docs: int = field(default=1)      # 최소 관련 문서 수
    
    # ========== 웹 검색 설정 ==========
    use_web_search: bool = field(default=True)     # 웹 검색 사용 여부
    web_search_when: str = field(default="no_docs")  # no_docs, low_score, always
    web_search_results: int = field(default=5)     # 웹 검색 결과 수
    
    # ========== 생성 설정 ==========
    max_context_length: int = field(default=2000)  # 최대 컨텍스트 길이
    include_sources: bool = field(default=True)    # 출처 포함 여부
    
    # ========== 답변 품질 검사 ==========
    check_answer_quality: bool = field(default=True)  # 답변 품질 검사 여부
    
    # ========== 재시도 설정 ==========
    max_rewrite_attempts: int = field(default=3)   # 최대 쿼리 재작성 시도 횟수
    timeout_seconds: int = field(default=30)       # 작업 타임아웃 (초)


# ============ UI 설정 ============
@dataclass
class UIConfig:
    """UI/UX 설정"""
    
    # ========== 테마 ==========
    theme: str = field(default="light")  # light, dark
    primary_color: str = field(default="#2196F3")
    accent_color: str = field(default="#FF9800")
    
    # ========== 레이아웃 ==========
    sidebar_width: str = field(default="300px")
    chat_history_lines: int = field(default=10)
    
    # ========== 표시 옵션 ==========
    show_sources: bool = field(default=True)
    show_debug_info: bool = field(default=False)
    show_stats: bool = field(default=False)
    show_sources_limit: int = field(default=5)
    
    # ========== 대화 ==========
    max_history_messages: int = field(default=100)


# ============ 로깅 설정 ============
@dataclass
class LoggingConfig:
    """로깅 설정"""
    level: str = field(default="INFO")
    log_file: str = field(default="./logs/app.log")
    max_file_size: int = field(default=10 * 1024 * 1024)  # 10MB
    backup_count: int = field(default=5)
    format: str = field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# ============ 공통 설정 통합 ============
@dataclass
class CommonConfig:
    """전체 공통 설정"""
    
    # 기본 설정
    environment: str = field(default="dev")
    project_name: str = field(default="RAG_Pipeline")
    version: str = field(default="1.0.0")
    
    # 하위 설정들
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'environment': self.environment,
            'project_name': self.project_name,
            'version': self.version,
            'data': {
                'data_dir': self.data.data_dir,
                'chunk_size': self.data.chunk_size,
                'chunk_overlap': self.data.chunk_overlap,
            },
            'model': {
                'embedding_model': self.model.embedding_model,
                'llm_model': self.model.llm_model,
                'temperature': self.model.llm_temperature,
            },
            'pipeline': {
                'top_k': self.pipeline.top_k,
                'relevance_threshold': self.pipeline.relevance_threshold,
                'use_web_search': self.pipeline.use_web_search,
            }
        }
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        try:
            self.model.validate()
            return True
        except ValueError as e:
            print(f"❌ 설정 오류: {e}")
            return False


# ============ 상수 정의 ============
class Constants:
    """프로젝트 전체 상수"""
    
    # 프롬프트 템플릿
    SYSTEM_PROMPT = """당신은 전문적이고 친절한 AI 어시스턴트입니다.
제공된 문맥을 기반으로 사용자의 질문에 정확하게 답변하세요.
모르는 내용은 명확하게 "알 수 없습니다"라고 말씀해주세요."""
    
    GRADE_PROMPT = """주어진 문서가 다음 질문과 관련이 있는지 판단하세요.
질문: {question}
문서: {document}
관련성 판정 (yes/no)을 한 단어로만 답변하세요."""
    
    # 성능 임계값
    SIMILARITY_THRESHOLD = 0.5
    RELEVANCE_THRESHOLD = 0.5
    
    # 제한값
    MAX_DOCUMENTS = 100
    MAX_QUERY_LENGTH = 1000
    MAX_RESPONSE_LENGTH = 5000
    
    # 타임아웃
    DEFAULT_TIMEOUT = 30  # 초
    EMBEDDING_TIMEOUT = 60
    LLM_TIMEOUT = 120
    
    # 일반적인 설정
    DEFAULT_LANGUAGE = "ko"
    SUPPORTED_LANGUAGES = ["ko", "en", "ja", "zh"]


# ============ 기본 설정 인스턴스 ============
# 프로젝트에서 사용할 기본 설정
DEFAULT_CONFIG = CommonConfig()


def get_config(env: str = "dev") -> CommonConfig:
    """환경에 맞는 설정 반환"""
    config = CommonConfig(environment=env)
    
    if env == "prod":
        config.logging.level = "WARNING"
        config.pipeline.check_answer_quality = True
        config.ui.show_debug_info = False
    elif env == "dev":
        config.logging.level = "DEBUG"
        config.ui.show_debug_info = True
    
    return config


