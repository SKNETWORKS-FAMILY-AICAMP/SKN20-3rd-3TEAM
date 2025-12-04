"""
공통 모듈 (Common Module)
=====================
프로젝트의 공통 디렉토리 모듈 뼈대
각 팀원이 여기서 고도화하고 싶은 부분을 맡아 보완합니다.

모듈 구조:
- base/: 기본 인터페이스 및 추상 클래스
- config/: 설정 및 상수
- utils/: 공통 유틸리티
- models/: 공통 데이터 모델
- pipelines/: RAG 파이프라인 기본 구현
- extensions/: 팀원별 고도화 확장 포인트
"""

from .base import (
    BaseRetriever,
    BaseRAGPipeline,
    BaseEmbedding,
    BaseVectorStore,
)
from .config import CommonConfig, ModelConfig, PipelineConfig
from .models import Document, QueryRequest, QueryResponse, SourceInfo
from .pipelines import SimpleRAGPipeline
from .utils import setup_logging

__version__ = "1.0.0"
__all__ = [
    "BaseRetriever",
    "BaseRAGPipeline",
    "BaseEmbedding",
    "BaseVectorStore",
    "CommonConfig",
    "ModelConfig",
    "PipelineConfig",
    "Document",
    "QueryRequest",
    "QueryResponse",
    "SourceInfo",
    "SimpleRAGPipeline",
    "setup_logging",
]


