"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api import api_router
from .services import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 이벤트"""
    # 시작 시 RAG 시스템 초기화
    print("=" * 60)
    print("FastAPI 서버 시작 중...")
    print("=" * 60)
    
    rag_service.initialize()
    
    print("=" * 60)
    print("FastAPI 서버 준비 완료!")
    print(f"Swagger UI: http://localhost:8000/docs")
    print("=" * 60)
    
    yield
    
    # 종료 시 정리 작업
    print("FastAPI 서버 종료 중...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="강아지 질병 증상 상담 챗봇 API - RAG 기반 질의응답 시스템",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Pet Health Chatbot API",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "chat": f"{settings.API_V1_STR}/chat",
            "search": f"{settings.API_V1_STR}/search",
            "health": f"{settings.API_V1_STR}/health"
        }
    }


@app.get("/health", tags=["monitoring"])
async def health():
    """간단한 헬스 체크"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
