"""
공통 데이터 모델
===============
전체 파이프라인에서 사용할 데이터 구조를 정의합니다.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============ 열거형 ============
class DocumentSource(Enum):
    """문서 출처"""
    INTERNAL = "internal"
    WEB = "web"
    DATABASE = "database"
    USER_UPLOADED = "user_uploaded"
    UNKNOWN = "unknown"


class SourceType(Enum):
    """출처 유형"""
    FILE = "file"
    URL = "url"
    DATABASE = "database"
    API = "api"


class QueryType(Enum):
    """질문 유형"""
    FACTUAL = "factual"          # 사실 기반
    REASONING = "reasoning"       # 추론 기반
    CREATIVE = "creative"         # 창의적
    CONVERSATIONAL = "conversational"  # 대화형


# ============ 문서 관련 모델 ============
@dataclass
class Document:
    """문서 모델"""
    id: str
    content: str
    title: Optional[str] = None
    source: DocumentSource = DocumentSource.INTERNAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    def truncate(self, max_length: int = 500) -> str:
        """내용을 지정된 길이로 축약"""
        if len(self.content) > max_length:
            return self.content[:max_length] + "..."
        return self.content


@dataclass
class SourceInfo:
    """출처 정보"""
    title: str                                  # 출처 제목
    url: Optional[str] = None                   # URL
    document_id: Optional[str] = None           # 문서 ID
    similarity_score: Optional[float] = None    # 유사도 점수
    relevance_score: Optional[float] = None     # 관련성 점수
    source_type: SourceType = SourceType.FILE   # 출처 유형
    metadata: Dict[str, Any] = field(default_factory=dict)  # 추가 정보
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'title': self.title,
            'url': self.url,
            'document_id': self.document_id,
            'similarity_score': self.similarity_score,
            'relevance_score': self.relevance_score,
            'source_type': self.source_type.value,
            'metadata': self.metadata,
        }


# ============ 질문/답변 모델 ============
@dataclass
class QueryRequest:
    """질문 요청"""
    query: str                                      # 사용자 질문
    query_type: QueryType = QueryType.FACTUAL      # 질문 유형
    language: str = "ko"                           # 언어
    top_k: int = 5                                 # 검색할 문서 수
    temperature: float = 0.7                       # LLM 창의성
    include_sources: bool = True                   # 출처 포함 여부
    include_debug_info: bool = False               # 디버그 정보 포함 여부
    session_id: Optional[str] = None               # 세션 ID
    user_id: Optional[str] = None                  # 사용자 ID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 추가 메타데이터
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'query': self.query,
            'query_type': self.query_type.value,
            'language': self.language,
            'top_k': self.top_k,
            'temperature': self.temperature,
            'include_sources': self.include_sources,
            'include_debug_info': self.include_debug_info,
        }


@dataclass
class QueryResponse:
    """질문 응답"""
    # 기본 응답
    query: str                                      # 원본 질문
    answer: str                                     # 생성된 답변
    
    # 출처 정보
    sources: List[SourceInfo] = field(default_factory=list)  # 참고 출처
    
    # 성능 정보
    response_time: Optional[float] = None           # 응답 시간 (초)
    retrieval_time: Optional[float] = None          # 검색 시간
    generation_time: Optional[float] = None         # 생성 시간
    
    # 디버그 정보
    debug_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 타임스탬프
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'query': self.query,
            'answer': self.answer,
            'sources': [s.to_dict() for s in self.sources],
            'response_time': self.response_time,
            'retrieval_time': self.retrieval_time,
            'generation_time': self.generation_time,
            'debug_info': self.debug_info,
            'metadata': self.metadata,
            'created_at': self.created_at,
        }
    
    def add_source(self, source: SourceInfo):
        """출처 추가"""
        self.sources.append(source)
    
    def to_json_string(self) -> str:
        """JSON 문자열로 변환"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# ============ 평가 모델 ============
@dataclass
class GradeResult:
    """문서 등급 평가 결과"""
    document_id: str                    # 문서 ID
    is_relevant: bool                   # 관련성 여부
    score: float                        # 점수 (0~1)
    reasoning: Optional[str] = None     # 판단 사유
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)


@dataclass
class PipelineMetrics:
    """파이프라인 메트릭"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time: float = 0.0
    average_retrieval_time: float = 0.0
    average_generation_time: float = 0.0
    average_sources_count: float = 0.0
    web_search_used_count: int = 0
    
    def success_rate(self) -> float:
        """성공률"""
        if self.total_queries == 0:
            return 0.0
        return self.successful_queries / self.total_queries
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'failed_queries': self.failed_queries,
            'success_rate': f"{self.success_rate() * 100:.2f}%",
            'average_response_time': f"{self.average_response_time:.2f}s",
            'average_retrieval_time': f"{self.average_retrieval_time:.2f}s",
            'average_generation_time': f"{self.average_generation_time:.2f}s",
            'average_sources_count': f"{self.average_sources_count:.2f}",
            'web_search_used_count': self.web_search_used_count,
        }


# ============ 대화 모델 ============
@dataclass
class ChatMessage:
    """채팅 메시지"""
    role: str                                       # user, assistant, system
    content: str                                    # 메시지 내용
    sources: List[SourceInfo] = field(default_factory=list)  # 출처 (assistant만)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'role': self.role,
            'content': self.content,
            'sources': [s.to_dict() for s in self.sources],
            'timestamp': self.timestamp,
            'metadata': self.metadata,
        }


@dataclass
class ChatHistory:
    """대화 기록"""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_message(self, message: ChatMessage):
        """메시지 추가"""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
    
    def add_user_message(self, content: str):
        """사용자 메시지 추가"""
        message = ChatMessage(role="user", content=content)
        self.add_message(message)
    
    def add_assistant_message(self, content: str, sources: List[SourceInfo] = None):
        """어시스턴트 메시지 추가"""
        sources = sources or []
        message = ChatMessage(role="assistant", content=content, sources=sources)
        self.add_message(message)
    
    def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """최근 메시지 반환"""
        return self.messages[-limit:]
    
    def clear(self):
        """기록 초기화"""
        self.messages = []
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'messages': [m.to_dict() for m in self.messages],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'message_count': len(self.messages),
        }


# ============ 에러 모델 ============
@dataclass
class ErrorInfo:
    """에러 정보"""
    error_type: str                         # 에러 타입
    message: str                            # 에러 메시지
    details: Optional[str] = None           # 상세 정보
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    suggestion: Optional[str] = None        # 해결 방법
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)


