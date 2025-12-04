"""
Streamlit 애플리케이션 설정 파일
RAG 파이프라인의 파라미터와 UI 설정을 관리
"""

from dataclasses import dataclass
from typing import Optional

# ==================== RAG 파이프라인 설정 ====================

@dataclass
class RAGConfig:
    """RAG 파이프라인 설정"""
    
    # 벡터 DB 설정
    persist_directory: str = "./chroma_db"
    collection_name: str = "rag_collection"
    
    # Retriever 설정
    top_k: int = 5  # 초기 검색 문서 수
    
    # LLM 설정
    llm_model: str = "gpt-4o-mini"  # "gpt-4o-mini", "gpt-4-turbo", "gpt-4o"
    temperature: float = 0.0  # 결정론적 답변 (0.0-1.0)
    
    # 임베딩 모델 설정
    embedding_model_type: str = "openai"  # "openai" 또는 "huggingface"
    embedding_model_name: Optional[str] = "text-embedding-3-small"
    
    # 웹 검색 설정
    enable_web_search: bool = True
    web_search_k: int = 3  # 웹 검색 결과 수
    
    # 디버그 설정
    debug_mode: bool = False  # Streamlit 환경에서는 항상 False 권장
    show_logs: bool = False


# ==================== Streamlit UI 설정 ====================

@dataclass
class StreamlitUIConfig:
    """Streamlit UI 설정"""
    
    # 페이지 설정
    page_title: str = "🏥 의료 RAG 챗봇"
    page_icon: str = "🏥"
    layout: str = "wide"  # "centered" 또는 "wide"
    
    # 색상 테마
    primary_color: str = "#2196F3"  # 파란색
    background_color: str = "#FFFFFF"  # 흰색
    secondary_bg_color: str = "#F8F9FA"  # 연한 회색
    
    # 채팅 UI 설정
    show_sources_default: bool = True  # 기본적으로 출처 표시
    show_debug_info_default: bool = False  # 기본적으로 디버그 정보 숨김
    show_thinking_process: bool = True  # 생각 과정 표시
    
    # 페이지네이션
    messages_per_page: int = 10
    enable_pagination: bool = True
    
    # 입력 설정
    placeholder_text: str = "예: 강아지 피부 질환의 증상은 무엇인가요?"
    max_input_length: int = 1000
    input_text_area_height: int = 100
    
    # 버튼 및 UI 요소
    show_example_questions: bool = True
    show_statistics: bool = True
    show_help: bool = True
    enable_export: bool = False  # 대화 내보내기
    
    # 세션 타임아웃 (초 단위)
    session_timeout: int = 1800  # 30분


# ==================== 예시 질문 ====================

EXAMPLE_QUESTIONS = [
    "강아지 피부 질환의 증상은 무엇인가요?",
    "벼룩 알러지성 피부염 치료법을 알려주세요",
    "개의 혈액형에 대해 설명해주세요",
    "면역 체계 질환의 종류는?",
    "개에서 감염병의 예방 방법은?",
    "알러지 반응의 단계를 설명해주세요",
    "자가면역질환에 대해 알려주세요",
    "면역결핍의 원인은 무엇인가요?",
]


# ==================== 디버그 정보 설정 ====================

@dataclass
class DebugConfig:
    """디버그 정보 표시 설정"""
    
    # 표시 항목
    show_similarity_scores: bool = True
    show_grade_results: bool = True
    show_web_search_info: bool = True
    show_processing_time: bool = True
    show_token_usage: bool = False  # OpenAI 토큰 사용량
    
    # 상세도 레벨 (1: 최소, 3: 최대)
    verbosity_level: int = 2


# ==================== 기본 설정 인스턴스 ====================

# 기본 RAG 설정
default_rag_config = RAGConfig()

# 기본 UI 설정
default_ui_config = StreamlitUIConfig()

# 기본 디버그 설정
default_debug_config = DebugConfig()


# ==================== 프리셋 설정 ====================

class RAGConfigPresets:
    """RAG 설정 프리셋"""
    
    @staticmethod
    def fast() -> RAGConfig:
        """빠른 응답 설정 (1-2초)"""
        return RAGConfig(
            llm_model="gpt-4o-mini",
            temperature=0.0,
            top_k=3,
            debug_mode=False
        )
    
    @staticmethod
    def balanced() -> RAGConfig:
        """균형잡힌 설정 (2-3초, 기본값)"""
        return RAGConfig(
            llm_model="gpt-4o-mini",
            temperature=0.0,
            top_k=5,
            debug_mode=False
        )
    
    @staticmethod
    def accurate() -> RAGConfig:
        """정확한 답변 설정 (3-5초)"""
        return RAGConfig(
            llm_model="gpt-4o",
            temperature=0.0,
            top_k=10,
            debug_mode=False
        )
    
    @staticmethod
    def creative() -> RAGConfig:
        """창의적인 답변 설정 (temperature > 0)"""
        return RAGConfig(
            llm_model="gpt-4o",
            temperature=0.7,
            top_k=5,
            debug_mode=False
        )
    
    @staticmethod
    def development() -> RAGConfig:
        """개발 모드 설정"""
        return RAGConfig(
            llm_model="gpt-4o-mini",
            temperature=0.0,
            top_k=5,
            debug_mode=True,
            show_logs=True
        )


# ==================== 함수 ====================

def get_config_description(preset_name: str) -> str:
    """프리셋 설명 반환"""
    descriptions = {
        "fast": "⚡ 빠른 응답 (1-2초)\n최소 리소스 사용, 기본 질문 추천",
        "balanced": "⚖️ 균형잡힌 (2-3초)\n대부분의 질문에 최적, 기본 설정",
        "accurate": "🎯 정확한 답변 (3-5초)\n최고 품질, 복잡한 질문 추천",
        "creative": "✨ 창의적 (3-5초)\n다양한 관점 제공, 낮은 온도",
        "development": "🐛 개발 모드\n로그 및 디버그 정보 포함",
    }
    return descriptions.get(preset_name, "알 수 없는 프리셋")


def validate_config(config: RAGConfig) -> bool:
    """설정 유효성 검사"""
    # Top-K 범위
    if not (1 <= config.top_k <= 20):
        raise ValueError("top_k는 1-20 사이여야 합니다")
    
    # Temperature 범위
    if not (0.0 <= config.temperature <= 1.0):
        raise ValueError("temperature는 0.0-1.0 사이여야 합니다")
    
    # LLM 모델 유효성
    valid_models = ["gpt-4o-mini", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
    if config.llm_model not in valid_models:
        raise ValueError(f"유효하지 않은 LLM 모델: {config.llm_model}")
    
    # 임베딩 모델 타입 유효성
    if config.embedding_model_type not in ["openai", "huggingface"]:
        raise ValueError("embedding_model_type은 'openai' 또는 'huggingface'여야 합니다")
    
    return True


# ==================== 예시 사용 ====================

if __name__ == "__main__":
    # 기본 설정 출력
    print("기본 RAG 설정:")
    print(f"  LLM 모델: {default_rag_config.llm_model}")
    print(f"  Top-K: {default_rag_config.top_k}")
    print(f"  Temperature: {default_rag_config.temperature}")
    print()
    
    # 프리셋 설정 출력
    print("사용 가능한 프리셋:")
    presets = ["fast", "balanced", "accurate", "creative", "development"]
    for preset in presets:
        print(f"  {preset}: {get_config_description(preset)}")
    print()
    
    # 프리셋 적용 예시
    print("프리셋 적용 예시:")
    fast_config = RAGConfigPresets.fast()
    print(f"  Fast 프리셋 - LLM: {fast_config.llm_model}, Top-K: {fast_config.top_k}")
    
    accurate_config = RAGConfigPresets.accurate()
    print(f"  Accurate 프리셋 - LLM: {accurate_config.llm_model}, Top-K: {accurate_config.top_k}")

