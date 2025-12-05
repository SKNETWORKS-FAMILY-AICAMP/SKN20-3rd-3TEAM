"""
FastAPI 서버 - 챗봇 API 엔드포인트
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.graph import graph
from app.config import settings


# FastAPI 앱 생성
app = FastAPI(
    title="강아지 증상 상담 챗봇 API",
    description="강아지 증상에 대한 상담과 동물병원 추천을 제공하는 RAG 기반 챗봇",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 요청/응답 모델
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    question: str = Field(..., description="사용자의 질문 (강아지 증상)")
    location: Optional[str] = Field(None, description="위치 정보 (예: '서울 강남구')")
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")
    radius: Optional[int] = Field(3000, description="검색 반경 (미터)")  # 🔧 추가

    class Config:
        json_schema_extra = {
            "example": {
                "question": "우리 강아지가 기침을 자주 하고 숨을 헐떡이는데 괜찮을까요?",
                "location": "서울 강남구",
                "radius": 3000
            }
        }


class HospitalInfo(BaseModel):
    """동물병원 정보 모델"""
    name: Optional[str] = None  # 🔧 Optional로 변경
    address: Optional[str] = None
    phone: Optional[str] = None
    map_url: Optional[str] = None
    distance_km: Optional[float] = None


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str = Field(..., description="전체 응답 텍스트")
    rag_response: str = Field(..., description="RAG 기반 증상 상담 응답")
    hospitals: List[HospitalInfo] = Field(default=[], description="추천 동물병원 리스트")  # 🔧 기본값 추가
    num_sources: int = Field(..., description="참고한 자료 수")
    source_type: str = Field(..., description="정보 출처 (vectordb, vectordb+websearch)")
    used_web_search: bool = Field(..., description="웹검색 사용 여부")
    web_search_count: int = Field(default=0, description="웹검색 결과 개수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "전체 통합 응답...",
                "rag_response": "RAG 기반 상담 내용...",
                "hospitals": [],
                "num_sources": 3,
                "source_type": "vectordb+websearch",
                "used_web_search": True,
                "web_search_count": 2
            }
        }


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "강아지 증상 상담 챗봇 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "챗봇 대화",
            "GET /health": "헬스 체크"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "model": settings.OPENAI_MODEL,
        "map_provider": settings.MAP_API_PROVIDER
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    챗봇 대화 엔드포인트

    Args:
        request: 사용자 질문 및 위치 정보

    Returns:
        ChatResponse: RAG 응답 + 동물병원 추천
    """
    try:
        # 초기 상태 구성
        initial_state = {
            "question": request.question,
            "location": request.location,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius": request.radius  # 🔧 추가
        }

        # 그래프 실행
        print(f"\n{'='*60}")
        print(f"새 요청: {request.question[:50]}...")
        print(f"{'='*60}")

        result = graph.invoke(initial_state)

        # 출처 정보 판단
        used_web_search = result.get("needs_web_search", False) and len(result.get("web_search_results", [])) > 0
        source_type = "vectordb+websearch" if used_web_search else "vectordb"
        
        # 🔧 hospitals 처리 - 항상 빈 리스트 반환 (병원 정보는 final_response에 포함)
        hospitals_list = []
        
        # 응답 구성
        response = ChatResponse(
            response=result["final_response"],
            rag_response=result["rag_response"],
            hospitals=hospitals_list,  # 🔧 빈 리스트
            num_sources=len(result["retrieved_docs"]),
            source_type=source_type,
            used_web_search=used_web_search,
            web_search_count=len(result.get("web_search_results", []))
        )

        print(f"✅ 응답 완료\n")
        return response

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )