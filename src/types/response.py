"""
Response 타입 정의

시스템이 반환하는 응답의 스키마를 정의합니다.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.types.document import Document


class RAGResponse(BaseModel):
    """
    RAG 파이프라인의 최종 응답

    Attributes:
        query: 원본 질문
        answer: 생성된 답변
        documents: 참고한 문서들
        intent: 질문의 분류 의도
        metadata: 응답 관련 메타데이터
    """

    query: str = Field(..., description="원본 질문")
    answer: str = Field(..., description="생성된 답변")
    documents: List[Document] = Field(default_factory=list, description="참고 문서들")
    intent: str = Field("unknown", description="질문 분류 의도")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    model: Optional[str] = Field(None, description="사용한 LLM 모델")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "query": "우리 강아지가 피부염이 있는데 어디 병원을 가야 하나요?",
                "answer": "피부염은 가려움증과 염증을 특징으로 합니다. 근처 동물병원에서 진료를 받으실 것을 권장드립니다.",
                "documents": [],
                "intent": "medical",
                "metadata": {},
                "model": "gpt-4",
                "execution_time": 2.5,
            }
        }

    def __repr__(self) -> str:
        return (
            f"RAGResponse(intent={self.intent}, "
            f"docs={len(self.documents)}, "
            f"time={self.execution_time:.2f}s)"
        )


class HospitalResponse(BaseModel):
    """
    병원 위치 안내 응답

    Attributes:
        query: 원본 질문
        hospitals: 검색된 병원 정보들
        location: 검색 위치 정보
    """

    query: str = Field(..., description="원본 질문")
    hospitals: List[Dict[str, Any]] = Field(
        default_factory=list, description="병원 정보 리스트"
    )
    location: Dict[str, Any] = Field(
        default_factory=dict, description="검색 위치 정보"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "query": "강남역 근처 동물병원",
                "hospitals": [
                    {
                        "name": "ABC 동물병원",
                        "address": "서울시 강남구 테헤란로 123",
                        "phone": "02-1234-5678",
                        "lat": 37.4979,
                        "lon": 127.0276,
                        "distance": 500,
                    }
                ],
                "location": {"region": "강남구", "landmark": "강남역"},
                "metadata": {},
            }
        }

    def __repr__(self) -> str:
        return (
            f"HospitalResponse(query={self.query[:30]}..., "
            f"hospitals={len(self.hospitals)})"
        )


class ErrorResponse(BaseModel):
    """
    에러 응답

    Attributes:
        error_code: 에러 코드
        error_message: 에러 메시지
        details: 추가 상세 정보
    """

    error_code: str = Field(..., description="에러 코드")
    error_message: str = Field(..., description="에러 메시지")
    details: Dict[str, Any] = Field(default_factory=dict, description="상세 정보")

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "error_code": "RETRIEVAL_FAILED",
                "error_message": "벡터 검색 중 오류가 발생했습니다.",
                "details": {"exception": "ConnectionError"},
            }
        }

    def __repr__(self) -> str:
        return f"ErrorResponse(code={self.error_code}, msg={self.error_message})"

