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


def get_embedding_model(model_type: str = "openai", model_name: Optional[str] = None):
    """
    임베딩 모델 인스턴스 생성
    
    Args:
        model_type: "openai" 또는 "huggingface"
        model_name: 모델 이름 (None이면 기본값 사용)
        
    Returns:
        Embeddings 객체
    """
    if model_type.lower() == "openai":
        if not model_name:
            model_name = "text-embedding-3-small"
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        return OpenAIEmbeddings(model=model_name)
    
    elif model_type.lower() == "huggingface":
        if not model_name:
            # 한국어 지원이 좋은 모델
            model_name = "jhgan/ko-sroberta-multitask"
        
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
    print(f"Creating vectorstore with {len(documents)} documents...")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    print(f"Vectorstore created and persisted to {persist_directory}")
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
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_name=collection_name
    )
    
    print(f"Vectorstore loaded from {persist_directory}")
    return vectorstore


if __name__ == "__main__":
    # 테스트
    from ingestion import ingest_data
    from chunking import chunk_documents_with_token_range
    
    # 환경변수 확인
    from dotenv import load_dotenv
    load_dotenv()
    
    # 데이터 로드 및 chunking
    data_dir = "../data/Validation/01.원천데이터"
    docs = ingest_data(data_dir)
    chunked = chunk_documents_with_token_range(docs)
    
    # 임베딩 모델 생성
    embedding_model = get_embedding_model("openai")
    
    # 벡터스토어 생성
    vectorstore = create_vectorstore(
        chunked,
        embedding_model,
        persist_directory="./test_chroma_db",
        collection_name="test_collection"
    )
    
    print(f"Vectorstore created successfully!")

