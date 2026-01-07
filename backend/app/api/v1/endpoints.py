"""
FastAPI v1 Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from ...models.schemas import (
    ChatRequest, ChatResponse,
    SearchRequest, SearchResponse,
    HealthResponse
)
from ...services import rag_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="채팅 질의응답")
async def chat_endpoint(request: ChatRequest):
    """
    강아지 질병 증상 질의응답 API
    
    - **question**: 사용자 질문
    - **search_type**: 검색 방식 (similarity/bm25/ensemble)
    - **k**: 검색할 문서 개수 (1-20)
    - **use_rewrite**: Query Rewriting 사용 여부
    
    Returns:
    - AI 답변
    - 참고 문서 목록
    - 사용된 검색 방식
    - 재작성된 질문 (사용 시)
    """
    try:
        result = await rag_service.chat(
            question=request.question,
            search_type=request.search_type,
            k=request.k,
            use_rewrite=request.use_rewrite
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채팅 처리 실패: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse, summary="문서 검색")
async def search_endpoint(request: SearchRequest):
    """
    문서 검색 API (답변 생성 없이 문서만 검색)
    
    - **query**: 검색 질의
    - **search_type**: 검색 방식
    - **k**: 검색할 문서 개수
    
    Returns:
    - 검색된 문서 목록
    - 검색 방식
    - 문서 개수
    """
    try:
        result = await rag_service.search_documents(
            query=request.query,
            search_type=request.search_type,
            k=request.k
        )
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 검색 실패: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, summary="헬스 체크")
async def health_check():
    """
    시스템 상태 확인 API
    
    Returns:
    - 서비스 상태
    - ChromaDB 상태
    - 모델 로드 상태
    - 벡터스토어 문서 개수
    """
    result = rag_service.health_check()
    return HealthResponse(**result)
