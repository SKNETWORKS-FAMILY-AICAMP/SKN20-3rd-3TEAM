"""
전역 설정 관리
환경 변수, 모델 설정, API 키 등을 관리합니다.
"""
import os
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM 설정"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None

    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv('OPENAI_API_KEY')


@dataclass
class RetrieverConfig:
    """검색기 설정"""
    top_k: int = 5
    score_threshold: float = 0.6
    web_search_enabled: bool = True
    tavily_api_key: Optional[str] = None

    def __post_init__(self):
        if not self.tavily_api_key:
            self.tavily_api_key = os.getenv('TAVILY_API_KEY')


@dataclass
class ExternalAPIConfig:
    """외부 API 설정"""
    kakao_map_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    def __post_init__(self):
        if not self.kakao_map_api_key:
            self.kakao_map_api_key = os.getenv('KAKAO_MAP_API_KEY')
        if not self.tavily_api_key:
            self.tavily_api_key = os.getenv('TAVILY_API_KEY')


@dataclass
class DataConfig:
    """데이터 설정"""
    hospital_json_path: str = "data/raw/hospital/서울시_동물병원_인허가_정보.json"
    vectorstore_path: str = "data/vectorstore"
    embedding_model: str = "text-embedding-3-small"


@dataclass
class Settings:
    """전체 설정"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    external_api: ExternalAPIConfig = field(default_factory=ExternalAPIConfig)
    data: DataConfig = field(default_factory=DataConfig)
    
    # 로깅 설정
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    debug_mode: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'


_settings: Optional[Settings] = None


def get_settings(force_reload: bool = False) -> Settings:
    """
    전역 설정 인스턴스 반환 (싱글톤 패턴)
    
    Args:
        force_reload: 강제 재로드 여부
        
    Returns:
        Settings 인스턴스
    """
    global _settings
    if _settings is None or force_reload:
        _settings = Settings()
    return _settings

