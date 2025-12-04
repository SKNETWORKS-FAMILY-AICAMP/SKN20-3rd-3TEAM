"""
Document 타입 정의

벡터 검색이나 RAG 파이프라인에서 사용되는 Document 객체의 스키마를 정의합니다.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    검색 결과로 반환되는 문서 객체

    Attributes:
        id: 문서 고유 ID
        content: 문서의 실제 내용
        metadata: 문서의 메타데이터 (소스, 제목, 카테고리 등)
        score: 관련성 점수 (0.0 ~ 1.0)
        source: 문서의 출처 (url, local_file, vector_db 등)
    """

    id: str = Field(..., description="문서 고유 ID")
    content: str = Field(..., description="문서 내용")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    score: Optional[float] = Field(None, description="관련성 점수 (0.0~1.0)")
    source: str = Field("unknown", description="문서 출처")

    class Config:
        """Pydantic 모델 설정"""

        json_schema_extra = {
            "example": {
                "id": "doc_001",
                "content": "반려견의 피부염은 가려움증과 염증을 특징으로 합니다...",
                "metadata": {
                    "title": "반려견 피부염 진단 및 치료",
                    "category": "medical",
                    "author": "수의사 김철수",
                },
                "score": 0.95,
                "source": "vector_db",
            }
        }

    def __repr__(self) -> str:
        return (
            f"Document(id={self.id}, source={self.source}, "
            f"score={self.score}, content_len={len(self.content)})"
        )


class DocumentBatch(BaseModel):
    """
    여러 문서를 담는 배치 객체

    Attributes:
        documents: Document 리스트
        total_count: 전체 문서 수
    """

    documents: List[Document] = Field(default_factory=list, description="문서 리스트")
    total_count: int = Field(0, description="전체 문서 수")

    def __len__(self) -> int:
        return len(self.documents)

    def __getitem__(self, idx: int) -> Document:
        return self.documents[idx]

    def __repr__(self) -> str:
        return f"DocumentBatch(count={len(self.documents)}, total={self.total_count})"

