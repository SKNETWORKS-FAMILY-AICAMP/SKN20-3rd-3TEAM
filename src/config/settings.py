"""
전역 설정 모듈

환경 변수를 로드하고 애플리케이션 전체에서 사용할 설정값을 관리합니다.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """애플리케이션 전역 설정 클래스"""

    # ============================================================
    # LLM 설정
    # ============================================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "placeholder-key")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

    # ============================================================
    # 벡터 데이터베이스 설정
    # ============================================================
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR", "./data/chroma_db"
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "pet_medical_docs"
    )

    # ============================================================
    # 웹 검색 API 설정
    # ============================================================
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "placeholder-key")
    GOOGLE_SEARCH_ENGINE_ID: str = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "placeholder-id")
    KAKAO_MAP_API_KEY: str = os.getenv("KAKAO_MAP_API_KEY", "placeholder-key")
    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID", "placeholder-id")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET", "placeholder-secret")

    # ============================================================
    # 시스템 설정
    # ============================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Seoul")

    # ============================================================
    # RAG 파이프라인 설정
    # ============================================================
    RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", "5"))
    RELEVANCE_THRESHOLD: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.5"))
    WEB_SEARCH_RESULTS_LIMIT: int = int(os.getenv("WEB_SEARCH_RESULTS_LIMIT", "5"))

    # ============================================================
    # 파일 경로
    # ============================================================
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DOCS_DIR: Path = DATA_DIR / "docs"

    @classmethod
    def create_directories(cls) -> None:
        """필요한 디렉토리 생성"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.DOCS_DIR.mkdir(exist_ok=True)
        Path(cls.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)


# 전역 설정 인스턴스
settings = Settings()

# 애플리케이션 시작 시 디렉토리 생성
settings.create_directories()

