"""
Streamlit UI 애플리케이션

반려동물 의료 RAG 기반 멀티채널 LLM 서비스의 사용자 인터페이스
"""

import streamlit as st
from datetime import datetime

from src.config.logger import get_logger
from src.orchestrator.query_orchestrator import QueryOrchestrator
from src.types.response import ErrorResponse, HospitalResponse, RAGResponse

logger = get_logger(__name__)


# ============================================================
# Streamlit 페이지 설정
# ============================================================
st.set_page_config(
    page_title="반려동물 의료 QA 시스템",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 커스텀 CSS
# ============================================================
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .medical-response {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .hospital-response {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .error-response {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .info-box {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 세션 상태 초기화
# ============================================================
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = QueryOrchestrator()
    logger.info("QueryOrchestrator initialized")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "settings" not in st.session_state:
    st.session_state.settings = {
        "show_debug_info": False,
        "max_results": 5,
    }


# ============================================================
# 헤더
# ============================================================
col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("# 🐾")

with col2:
    st.title("반려동물 의료 QA + 병원 안내 시스템")

st.markdown(
    """
    **AI 기반 멀티채널 LLM 서비스**
    
    반려동물의 의료 문제 상담, 동물병원 위치 안내, 일반 정보를 제공합니다.
    """
)

st.divider()


# ============================================================
# 사이드바: 설정
# ============================================================
with st.sidebar:
    st.header("⚙️ 설정")

    st.session_state.settings["show_debug_info"] = st.checkbox(
        "디버그 정보 표시", 
        value=st.session_state.settings["show_debug_info"]
    )

    st.session_state.settings["max_results"] = st.slider(
        "최대 결과 개수",
        min_value=1,
        max_value=10,
        value=st.session_state.settings["max_results"],
    )

    st.divider()

    # 채팅 히스토리 관리
    st.subheader("💬 채팅 히스토리")

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    if len(st.session_state.chat_history) > 0:
        st.caption(f"대화 수: {len(st.session_state.chat_history)}")

        with st.expander("이전 대화 보기"):
            for idx, msg in enumerate(st.session_state.chat_history):
                st.caption(f"{idx + 1}. {msg['question'][:50]}...")

    st.divider()

    # 시스템 정보
    st.subheader("ℹ️ 시스템 정보")
    health_check = st.session_state.orchestrator.get_statistics()

    st.metric("총 쿼리", health_check.get("total_queries", 0))
    st.metric(
        "성공률", 
        f"{health_check.get('success_rate', 0) * 100:.1f}%"
    )

    # 도움말
    st.divider()
    st.subheader("❓ 사용 가이드")
    st.markdown(
        """
        **질문 예시:**
        - 의료: "우리 강아지가 피부염이 있는데 어떻게 하죠?"
        - 병원: "강남역 근처 동물병원 찾아줄래?"
        - 일반: "반려견 예방접종은 언제 해야 하나요?"
        """
    )


# ============================================================
# 메인 콘텐츠: 채팅 인터페이스
# ============================================================
st.subheader("💬 대화하기")

# 대화 히스토리 표시
conversation_container = st.container()

with conversation_container:
    for msg in st.session_state.chat_history:
        # 사용자 질문
        with st.chat_message("user"):
            st.write(msg["question"])

        # AI 응답
        response_data = msg["response"]
        response_type = msg.get("type", "rag")

        if response_type == "rag":
            with st.chat_message("assistant"):
                st.markdown(response_data.answer)

                # 참고 문서 표시
                if response_data.documents:
                    with st.expander("📚 참고 문서"):
                        for doc in response_data.documents:
                            st.markdown(f"**{doc.metadata.get('title', 'Unknown')}**")
                            st.caption(doc.content[:200] + "...")
                            st.caption(f"출처: {doc.source}")

                # 디버그 정보
                if st.session_state.settings["show_debug_info"]:
                    with st.expander("🔧 디버그 정보"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("의도", response_data.intent)
                        with col2:
                            st.metric(
                                "실행 시간",
                                f"{response_data.execution_time:.2f}s" if response_data.execution_time else "N/A"
                            )

        elif response_type == "hospital":
            with st.chat_message("assistant"):
                # 병원 정보 표시
                if response_data.hospitals:
                    st.markdown("### 🏥 검색된 병원")
                    for hospital in response_data.hospitals:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{hospital.get('name', 'Unknown')}**")
                            st.caption(hospital.get('address', '주소 미정보'))
                            st.caption(f"📞 {hospital.get('phone', 'N/A')}")
                        with col2:
                            distance = hospital.get("distance", 0)
                            st.metric(
                                "거리",
                                f"{distance/1000:.1f}km" if distance > 0 else "N/A"
                            )
                else:
                    st.warning("검색된 병원이 없습니다.")

        elif response_type == "error":
            with st.chat_message("assistant"):
                st.error(f"❌ {response_data.error_message}")

        st.divider()


# ============================================================
# 입력창
# ============================================================
st.subheader("🤔 질문하기")

col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "질문을 입력하세요:",
        placeholder="예: 우리 강아지가 피부염이 있는데 어디 병원을 가야 하나요?",
        label_visibility="collapsed",
    )

with col2:
    send_button = st.button("📤 전송", use_container_width=True)

# ============================================================
# 질문 처리
# ============================================================
if send_button and user_input:
    logger.info(f"Processing user input: {user_input}")

    # 진행 상황 표시
    with st.spinner("🔍 처리 중..."):
        try:
            # 오케스트레이터를 통한 처리
            result = st.session_state.orchestrator.process(user_input)

            response_type = result.get("type", "error")
            response_data = result.get("data")

            # 채팅 히스토리 저장
            st.session_state.chat_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "question": user_input,
                    "response": response_data,
                    "type": response_type,
                }
            )

            logger.info(f"Response type: {response_type}")

        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")

    # 페이지 새로고침
    st.rerun()


# ============================================================
# 푸터
# ============================================================
st.divider()

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.caption("🐾 Pet Medical RAG System")

with col2:
    st.caption(f"v0.1.0 | {datetime.now().strftime('%Y-%m-%d')}")

with col3:
    st.caption("Made with ❤️ by RAG Team")

