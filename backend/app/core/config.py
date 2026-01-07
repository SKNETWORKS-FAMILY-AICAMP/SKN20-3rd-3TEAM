"""
Configuration Settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    PROJECT_NAME: str = "Pet Health Chatbot API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI API
    OPENAI_API_KEY: str
    
    # LangSmith (선택)
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_TRACING_V2: str = "false"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_PROJECT: str = "pet_rag"
    
    # ChromaDB 설정
    VECTORSTORE_PATH: str = "../data/ChromaDB_bge_m3"
    COLLECTION_NAME: str = "pet_health_qa_system_bge_m3"
    
    # LLM 설정
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    
    # Embedding 모델
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
