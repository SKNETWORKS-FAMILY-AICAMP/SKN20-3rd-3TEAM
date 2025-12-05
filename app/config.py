"""
설정 파일 - 환경변수 및 상수 관리
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """환경변수 기반 설정 클래스"""
    
    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Tavily 웹검색 설정
    TAVILY_API_KEY: str = ""
    
    # 지도 API 설정
    MAP_API_PROVIDER: Literal["kakao", "naver", "google"] = "kakao"
    KAKAO_REST_API_KEY: str = ""
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    
    # 경로 설정
    VECTOR_STORE_PATH: str = "./data/vector_store"
    JSON_DATA_PATH: str = "./data/raw_json"
    
    # RAG 설정
    RETRIEVAL_TOP_K: int = 3
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TEMPERATURE: float = 0.3
    
    # 웹검색 설정
    WEB_SEARCH_ENABLED: bool = True
    RELEVANCE_THRESHOLD: float = 0.5
    
    # 타임아웃 설정 (추가)
    REQUEST_TIMEOUT: int = 30
    WEB_SEARCH_TIMEOUT: int = 10
    LLM_TIMEOUT: int = 15
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스 (이 부분이 중요!)
settings = Settings()

# 경로 상수
BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = BASE_DIR / settings.VECTOR_STORE_PATH
JSON_DATA_DIR = BASE_DIR / settings.JSON_DATA_PATH

# 디렉토리 생성
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
JSON_DATA_DIR.mkdir(parents=True, exist_ok=True)