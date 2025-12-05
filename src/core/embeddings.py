"""
Embeddings 모듈
OpenAI 또는 HuggingFace embeddings 모델 설정 및 Chroma DB 초기화
"""
import os
from typing import Optional, List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)


def get_embedding_model(model_type: str = "openai", model_name: Optional[str] = None):
    """
    임베딩 모델 인스턴스 생성
    
    Args:
        model_type: "openai" 또는 "huggingface"
        model_name: 모델 이름 (None이면 기본값 사용)
        
    Returns:
        Embeddings 객체
    """
    settings = get_settings()
    
    if model_type.lower() == "openai":
        if not model_name:
            model_name = settings.data.embedding_model
        
        api_key = settings.llm.api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        logger.info(f"OpenAI 임베딩 모델 로드: {model_name}")
        return OpenAIEmbeddings(model=model_name)
    
    elif model_type.lower() == "huggingface":
        if not model_name:
            # 한국어 지원이 좋은 모델
            model_name = "jhgan/ko-sroberta-multitask"
        
        logger.info(f"HuggingFace 임베딩 모델 로드: {model_name}")
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    else:
        raise ValueError(f"지원하지 않는 모델 타입: {model_type}")


def create_vectorstore(
    documents: List[Document],
    embedding_model,
    persist_directory: str = "./chroma_db",
    collection_name: str = "rag_collection"
) -> Chroma:
    """
    Chroma 벡터 DB 생성 및 문서 임베딩 저장
    
    Args:
        documents: Document 객체 리스트
        embedding_model: 임베딩 모델
        persist_directory: 벡터 DB 저장 디렉토리
        collection_name: 컬렉션 이름
        
    Returns:
        Chroma 벡터스토어 객체
    """
    logger.info(f"벡터스토어 생성 중: {len(documents)}개 문서")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    logger.info(f"벡터스토어 생성 완료: {persist_directory}")
    return vectorstore


def load_vectorstore(
    embedding_model,
    persist_directory: str = "./chroma_db",
    collection_name: str = "rag_collection"
) -> Chroma:
    """
    기존 Chroma 벡터 DB 로드
    
    Args:
        embedding_model: 임베딩 모델
        persist_directory: 벡터 DB 저장 디렉토리
        collection_name: 컬렉션 이름
        
    Returns:
        Chroma 벡터스토어 객체
    """
    logger.info(f"벡터스토어 로드 중: {persist_directory}")
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_name=collection_name
    )
    
    logger.info(f"벡터스토어 로드 완료")
    return vectorstore

