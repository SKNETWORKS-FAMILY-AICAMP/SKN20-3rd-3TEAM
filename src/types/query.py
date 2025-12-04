"""
Query 타입 정의

사용자 질문과 관련된 데이터 구조를 정의합니다.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Query(BaseModel):
    """
    사용자 질문을 나타내는 객체

    Attributes:
        text: 사용자의 원본 질문
        intent: 분류된 의도 ("medical", "hospital", "general", "unknown")
        metadata: 추가 컨텍스트 정보 (사용자 정보, 세션 정보 등)
        language: 질문 언어 (기본값: "ko")
    """

    text: str = Field(..., description="사용자 질문 텍스트")
    intent: Optional[str] = Field(None, description="분류된 의도")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="추가 메타데이터"
    )
    language: str = Field("ko", description="질문 언어")
    session_id: Optional[str] = Field(None, description="세션 ID")

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "text": "우리 강아지가 피부염이 있는데 어디 병원을 가야 하나요?",
                "intent": "medical",
                "metadata": {"user_id": "user_001", "location": "서울"},
                "language": "ko",
                "session_id": "session_123",
            }
        }

    def __repr__(self) -> str:
        return f'Query(intent={self.intent}, text="{self.text[:50]}...")'


class ClassificationResult(BaseModel):
    """
    의도 분류 결과

    Attributes:
        query: 원본 Query 객체
        intent: 분류된 의도
        confidence: 분류 신뢰도 (0.0 ~ 1.0)
        details: 분류 관련 상세 정보
    """

    query: Query = Field(..., description="원본 질문")
    intent: str = Field(..., description="분류된 의도")
    confidence: float = Field(..., description="신뢰도 점수")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="분류 상세 정보"
    )

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "query": {
                    "text": "우리 강아지가 피부염이 있는데 어디 병원을 가야 하나요?",
                    "intent": None,
                    "metadata": {},
                    "language": "ko",
                },
                "intent": "medical",
                "confidence": 0.95,
                "details": {"rule_matched": "contains_medical_keywords"},
            }
        }

    def __repr__(self) -> str:
        return (
            f"ClassificationResult(intent={self.intent}, "
            f"confidence={self.confidence:.2f})"
        )

