"""
Pydantic Models for Request/Response
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    question: str = Field(..., description="사용자 질문", min_length=1)
    search_type: str = Field(
        default="ensemble",
        description="검색 방식: similarity, bm25, ensemble"
    )
    k: int = Field(default=5, description="검색할 문서 개수", ge=1, le=20)
    use_rewrite: bool = Field(default=False, description="Query Rewriting 사용 여부")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "강아지가 기침을 해요",
                "search_type": "ensemble",
                "k": 5,
                "use_rewrite": False
            }
        }


class DocumentInfo(BaseModel):
    """문서 정보 모델"""
    content: str = Field(..., description="문서 내용")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    source_type: Optional[str] = Field(None, description="문서 타입 (medical_data/qa_data)")
    

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    answer: str = Field(..., description="AI 답변")
    sources: List[DocumentInfo] = Field(default_factory=list, description="참고 문서들")
    search_type: str = Field(..., description="사용된 검색 방식")
    rewritten_query: Optional[str] = Field(None, description="재작성된 질문")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "강아지 기침은 다양한 원인이 있을 수 있습니다...",
                "sources": [
                    {
                        "content": "Q: 강아지가 기침해요...",
                        "metadata": {"department": "내과", "disease": "기침"},
                        "source_type": "qa_data"
                    }
                ],
                "search_type": "ensemble",
                "rewritten_query": None
            }
        }


class SearchRequest(BaseModel):
    """문서 검색 요청"""
    query: str = Field(..., description="검색 질의", min_length=1)
    search_type: str = Field(default="ensemble", description="검색 방식")
    k: int = Field(default=5, description="검색할 문서 개수", ge=1, le=20)


class SearchResponse(BaseModel):
    """문서 검색 응답"""
    documents: List[DocumentInfo] = Field(..., description="검색된 문서들")
    search_type: str = Field(..., description="사용된 검색 방식")
    total_count: int = Field(..., description="검색된 문서 개수")


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str = Field(..., description="서비스 상태")
    chromadb_status: str = Field(..., description="ChromaDB 상태")
    model_loaded: bool = Field(..., description="모델 로드 상태")
    vectorstore_count: Optional[int] = Field(None, description="벡터스토어 문서 개수")
