"""
헬퍼 함수 모듈
문서 포매팅, 설정 관리 등
"""

from typing import List
from langchain_core.documents import Document


def format_documents(docs: List[Document]) -> str:
    """
    문서 리스트를 컨텍스트 문자열로 포매팅
    
    Args:
        docs: Document 리스트
        
    Returns:
        포매팅된 컨텍스트 문자열
    """
    if not docs:
        return ""
    
    formatted_parts = []
    for i, doc in enumerate(docs, 1):
        source_type = doc.metadata.get('source_type', 'unknown')
        
        # 문서 정보 헤더
        header = f"\n[문서 {i}] (출처 유형: {source_type})"
        
        # 메타데이터 정보
        metadata_str = ""
        if source_type == 'qa_data':
            life_stage = doc.metadata.get('life_stage', 'N/A')
            department = doc.metadata.get('department', 'N/A')
            disease = doc.metadata.get('disease', 'N/A')
            metadata_str = f"생애주기: {life_stage} / 과: {department} / 질병: {disease}"
        elif source_type == 'medical_data':
            book = doc.metadata.get('book_title', 'N/A')
            author = doc.metadata.get('author', 'N/A')
            publisher = doc.metadata.get('publisher', 'N/A')
            metadata_str = f"책: {book} / 저자: {author} / 출판사: {publisher}"
        
        # 본문
        content = doc.page_content
        
        # 조합
        if metadata_str:
            formatted_parts.append(f"{header}\n{metadata_str}\n내용: {content}")
        else:
            formatted_parts.append(f"{header}\n내용: {content}")
    
    return "\n---\n".join(formatted_parts)


def get_source_info(doc: Document) -> str:
    """
    문서의 출처 정보를 요약 문자열로 반환
    
    Args:
        doc: Document 객체
        
    Returns:
        출처 정보 문자열
    """
    source_type = doc.metadata.get('source_type', 'unknown')
    
    if source_type == 'qa_data':
        life_stage = doc.metadata.get('life_stage', 'N/A')
        department = doc.metadata.get('department', 'N/A')
        disease = doc.metadata.get('disease', 'N/A')
        return f"QA 데이터 ({life_stage} / {department} / {disease})"
    
    elif source_type == 'medical_data':
        book = doc.metadata.get('book_title', 'N/A')
        author = doc.metadata.get('author', 'N/A')
        publisher = doc.metadata.get('publisher', 'N/A')
        return f"서적 ({book} / {author} / {publisher})"
    
    return "출처 정보 없음"


def create_chat_history_context(history: List[tuple]) -> str:
    """
    채팅 히스토리를 컨텍스트 문자열로 변환
    
    Args:
        history: [(user_msg, bot_msg), ...] 형태의 리스트
        
    Returns:
        포매팅된 히스토리 문자열
    """
    if not history:
        return ""
    
    formatted = []
    for user_msg, bot_msg in history:
        formatted.append(f"사용자: {user_msg}")
        formatted.append(f"어시스턴트: {bot_msg}")
    
    return "\n".join(formatted)
