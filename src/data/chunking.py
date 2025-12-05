"""
Chunking 모듈
문단 기준 chunking (300-500 tokens, overlap 20-30%)
"""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils import get_logger

logger = get_logger(__name__)


def count_tokens(text: str, embedding_model=None) -> int:
    """
    텍스트의 토큰 수를 대략적으로 계산
    (한국어와 영어를 고려한 추정)
    
    Args:
        text: 텍스트 문자열
        embedding_model: 임베딩 모델 (현재는 사용하지 않음)
        
    Returns:
        토큰 수 (대략적)
    """
    # 간단한 추정: 한국어는 평균 1.5자당 1토큰, 영어는 4자당 1토큰
    korean_chars = sum(1 for c in text if ord(c) >= 0xAC00 and ord(c) <= 0xD7A3)
    other_chars = len(text) - korean_chars
    
    # 대략적인 토큰 수 계산
    estimated_tokens = int(korean_chars / 1.5 + other_chars / 4)
    return max(estimated_tokens, 1)  # 최소 1 토큰


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 400,
    chunk_overlap: int = 100,
    use_token_count: bool = True
) -> List[Document]:
    """
    문서들을 문단 기준으로 chunking
    
    Args:
        documents: Document 객체 리스트
        chunk_size: 청크 크기 (토큰 수, 기본값 400)
        chunk_overlap: 오버랩 크기 (토큰 수, 기본값 100, 약 25%)
        use_token_count: 토큰 수 기준 사용 여부
        
    Returns:
        Chunked Document 객체 리스트
    """
    logger.info(f"청킹 시작: {len(documents)}개 문서, chunk_size={chunk_size}")
    
    # RecursiveCharacterTextSplitter 설정
    # 문단 기준으로 분할하기 위해 separators 우선순위 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n\n",  # 큰 문단 구분
            "\n\n",    # 문단 구분
            "\n",      # 줄 구분
            ". ",      # 문장 구분
            " ",       # 단어 구분
            ""         # 문자 구분
        ],
        length_function=len,  # 문자 수 기준 (토큰 수는 추정이므로 문자 수 사용)
    )
    
    # 모든 문서를 chunking
    chunked_docs = []
    
    for doc in documents:
        # 원본 메타데이터 유지
        chunks = text_splitter.split_documents([doc])
        
        # 각 chunk에 원본 정보 추가
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'original_source': doc.metadata.get('source_path', 'unknown')
            })
        
        chunked_docs.extend(chunks)
    
    # 토큰 수 기준으로 재조정 (필요한 경우)
    if use_token_count:
        logger.debug("토큰 기준 재조정 진행 중...")
        final_chunks = []
        for chunk in chunked_docs:
            # 대략적인 토큰 수 추정
            estimated_tokens = count_tokens(chunk.page_content)
            
            # 토큰 수가 너무 크면 다시 분할
            if estimated_tokens > chunk_size * 1.5:
                # 더 작은 크기로 재분할
                small_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=int(chunk_size * 0.8),
                    chunk_overlap=int(chunk_overlap * 0.8),
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                sub_chunks = small_splitter.split_documents([chunk])
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        logger.info(f"청킹 완료: {len(final_chunks)}개 청크")
        return final_chunks
    
    logger.info(f"청킹 완료: {len(chunked_docs)}개 청크")
    return chunked_docs


def chunk_documents_with_token_range(
    documents: List[Document],
    min_tokens: int = 300,
    max_tokens: int = 500,
    overlap_ratio: float = 0.25
) -> List[Document]:
    """
    토큰 범위를 지정하여 chunking (300-500 tokens, overlap 20-30%)
    
    Args:
        documents: Document 객체 리스트
        min_tokens: 최소 토큰 수 (기본값 300)
        max_tokens: 최대 토큰 수 (기본값 500)
        overlap_ratio: 오버랩 비율 (기본값 0.25 = 25%)
        
    Returns:
        Chunked Document 객체 리스트
    """
    # 평균 토큰 수 계산
    avg_tokens = (min_tokens + max_tokens) // 2
    overlap_tokens = int(avg_tokens * overlap_ratio)
    
    logger.info(f"토큰 범위 청킹: {min_tokens}-{max_tokens} tokens, overlap_ratio={overlap_ratio}")
    
    return chunk_documents(
        documents,
        chunk_size=avg_tokens,
        chunk_overlap=overlap_tokens,
        use_token_count=True
    )

