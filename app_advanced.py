"""
Streamlit 기반 RAG 웹 애플리케이션 - 고급 버전
고급 기능: 설정 프리셋, 성능 모니터링, 내보내기, 등

사용법:
  streamlit run app_advanced.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import time
import json
from datetime import datetime

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# Streamlit 임포트
import streamlit as st
from streamlit.logger import get_logger

# 프로젝트 모듈 임포트
sys.path.insert(0, str(Path(__file__).parent))
from src.embeddings import get_embedding_model, load_vectorstore
from src.retrieval import create_retriever
from src.pipeline import LangGraphRAGPipeline
from streamlit_config import (
    RAGConfig, StreamlitUIConfig, RAGConfigPresets,
    default_rag_config, default_ui_config, default_debug_config,
    EXAMPLE_QUESTIONS, get_config_description
)

# 로거 설정
logger = get_logger(__name__)

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="🏥 의료 RAG 챗봇 (고급)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 메인 컨테이너 */
    .main {
        max-width: 1200px;
    }
    
    /* 채팅 메시지 스타일 */
    .chat-user {
        background-color: #E3F2FD;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
    }
    
    .chat-assistant {
        background-color: #F5F5F5;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    
    /* 소스 정보 */
    .source-box {
        background-color: #FFF3E0;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #FF9800;
        font-size: 0.9em;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background-color: #F9F9F9;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin: 10px 0;
    }
    
    /* 프리셋 버튼 */
    .preset-button {
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 초기화 함수 ====================

@st.cache_resource
def initialize_rag_pipeline(config: RAGConfig = None):
    """RAG 파이프라인 초기화"""
    if config is None:
        config = default_rag_config
    
    try:
        with st.spinner("🔄 RAG 시스템 초기화 중..."):
            # 임베딩 모델 로드
            embedding_model = get_embedding_model(
                config.embedding_model_type,
                config.embedding_model_name
            )
            
            # 벡터스토어 로드
            vectorstore = load_vectorstore(
                embedding_model,
                persist_directory=config.persist_directory,
                collection_name=config.collection_name
            )
            
            # Retriever 생성
            retriever = create_retriever(
                vectorstore,
                top_k=config.top_k
            )
            
            # RAG 파이프라인 생성
            pipeline = LangGraphRAGPipeline(
                retriever,
                llm_model=config.llm_model,
                temperature=config.temperature,
                debug=config.debug_mode
            )
            
        st.success("✅ RAG 시스템 준비 완료!")
        return pipeline
    
    except Exception as e:
        st.error(f"❌ RAG 시스템 초기화 실패: {str(e)}")
        logger.error(f"RAG initialization error: {str(e)}")
        return None


def initialize_session_state():
    """세션 상태 초기화"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    
    if "rag_config" not in st.session_state:
        st.session_state.rag_config = default_rag_config
    
    if "ui_config" not in st.session_state:
        st.session_state.ui_config = default_ui_config
    
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    
    if "show_debug_info" not in st.session_state:
        st.session_state.show_debug_info = False
    
    if "show_stats" not in st.session_state:
        st.session_state.show_stats = False
    
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = time.time()


# ==================== 메시지 표시 함수 ====================

def display_chat_message(role: str, content: str, sources: List[Dict] = None, elapsed_time: float = 0):
    """채팅 메시지 표시"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-user">
            <strong>👤 당신:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    elif role == "assistant":
        col1, col2 = st.columns([15, 1])
        with col1:
            st.markdown(f"""
            <div class="chat-assistant">
                <strong>🤖 AI 어시스턴트:</strong><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if elapsed_time > 0:
                st.metric("⏱️", f"{elapsed_time:.2f}s")
        
        # 출처 정보
        if sources and len(sources) > 0:
            with st.expander(f"📚 참고한 문서 ({len(sources)}개)"):
                for i, source in enumerate(sources, 1):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**[{i}]**")
                    with col2:
                        source_type = source.get('type', 'internal')
                        type_icon = '🌐' if source_type == 'web' else '📄'
                        st.markdown(f"""
                        {type_icon} **{source.get('file_name', 'Unknown')}**
                        - 부서: {source.get('department', 'N/A')}
                        - 제목: {source.get('title', 'N/A')}
                        """)


def display_chat_history():
    """대화 기록 표시"""
    if not st.session_state.chat_history:
        st.info("💬 아직 대화가 없습니다. 질문을 입력해주세요!")
        return
    
    for message in st.session_state.chat_history:
        role = message.get("role")
        content = message.get("content")
        sources = message.get("sources", [])
        elapsed_time = message.get("elapsed_time", 0)
        
        display_chat_message(role, content, sources, elapsed_time)


# ==================== 질문 처리 ====================

def process_question(question: str) -> Dict[str, Any]:
    """질문 처리"""
    try:
        with st.spinner("🔄 답변을 생성 중입니다..."):
            start_time = time.time()
            result = st.session_state.pipeline.rag_pipeline_with_sources(question)
            elapsed_time = time.time() - start_time
            
            result['elapsed_time'] = elapsed_time
            return result
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'answer': f"❌ 오류 발생: {str(e)}",
            'sources': [],
            'elapsed_time': 0
        }


def handle_question_submission():
    """질문 제출 핸들러"""
    question = st.session_state.user_input.strip()
    
    if not question:
        st.warning("⚠️ 질문을 입력해주세요!")
        return
    
    if st.session_state.pipeline is None:
        st.error("❌ RAG 시스템이 준비되지 않았습니다.")
        return
    
    # 대화 기록에 질문 추가
    st.session_state.chat_history.append({
        "role": "user",
        "content": question,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # 질문 처리
    result = process_question(question)
    
    # 대화 기록에 답변 추가
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result.get('answer', '답변을 생성할 수 없습니다.'),
        "sources": result.get('sources', []),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_time": result.get('elapsed_time', 0),
        "debug_info": {
            "document_scores": result.get('document_scores', []),
            "grade_results": result.get('grade_results', []),
            "web_search_needed": result.get('web_search_needed', 'No')
        }
    })
    
    st.session_state.user_input = ""
    st.rerun()


# ==================== 사이드바 ====================

def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 탭 설정
        tab1, tab2, tab3 = st.tabs(["🔧 시스템", "⚡ 성능", "📊 통계"])
        
        with tab1:
            st.subheader("시스템 상태")
            if st.session_state.pipeline:
                st.success("✅ RAG 시스템 준비됨")
            else:
                st.error("❌ RAG 시스템 준비 중...")
            
            st.subheader("설정 프리셋")
            preset_selected = st.radio(
                "프리셋 선택:",
                ["balanced", "fast", "accurate", "creative"],
                format_func=lambda x: f"{x} - {get_config_description(x).split(chr(10))[0]}"
            )
            
            if st.button("✅ 프리셋 적용"):
                if preset_selected == "fast":
                    st.session_state.rag_config = RAGConfigPresets.fast()
                elif preset_selected == "balanced":
                    st.session_state.rag_config = RAGConfigPresets.balanced()
                elif preset_selected == "accurate":
                    st.session_state.rag_config = RAGConfigPresets.accurate()
                elif preset_selected == "creative":
                    st.session_state.rag_config = RAGConfigPresets.creative()
                
                st.session_state.pipeline = None  # 파이프라인 재초기화
                st.rerun()
            
            st.subheader("표시 옵션")
            st.session_state.show_sources = st.checkbox(
                "출처 정보 표시",
                value=st.session_state.show_sources
            )
            st.session_state.show_debug_info = st.checkbox(
                "디버그 정보 표시",
                value=st.session_state.show_debug_info
            )
        
        with tab2:
            st.subheader("LLM 모델")
            models = ["gpt-4o-mini", "gpt-4-turbo", "gpt-4o"]
            selected_model = st.selectbox(
                "모델 선택:",
                models,
                index=models.index(st.session_state.rag_config.llm_model)
            )
            
            if selected_model != st.session_state.rag_config.llm_model:
                st.session_state.rag_config.llm_model = selected_model
                st.session_state.pipeline = None
                st.info("설정이 변경되었습니다. 새로고침 후 적용됩니다.")
            
            st.subheader("Retriever 설정")
            top_k = st.slider(
                "Top-K:",
                min_value=1,
                max_value=20,
                value=st.session_state.rag_config.top_k,
                step=1
            )
            
            if top_k != st.session_state.rag_config.top_k:
                st.session_state.rag_config.top_k = top_k
                st.session_state.pipeline = None
            
            temperature = st.slider(
                "Temperature (창의성):",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.rag_config.temperature,
                step=0.1
            )
            
            if temperature != st.session_state.rag_config.temperature:
                st.session_state.rag_config.temperature = temperature
                st.session_state.pipeline = None
            
            st.subheader("고급 옵션")
            st.session_state.rag_config.enable_web_search = st.checkbox(
                "웹 검색 활성화",
                value=st.session_state.rag_config.enable_web_search
            )
        
        with tab3:
            st.subheader("대화 관리")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ 대화 초기화"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("📊 통계 보기"):
                    st.session_state.show_stats = True
            
            st.subheader("세션 정보")
            session_duration = time.time() - st.session_state.session_start_time
            minutes = int(session_duration // 60)
            seconds = int(session_duration % 60)
            st.markdown(f"""
            - **세션 시간**: {minutes}분 {seconds}초
            - **총 질문**: {sum(1 for msg in st.session_state.chat_history if msg['role'] == 'user')}개
            - **평균 응답**: {sum(msg.get('elapsed_time', 0) for msg in st.session_state.chat_history if msg['role'] == 'assistant') / max(1, sum(1 for msg in st.session_state.chat_history if msg['role'] == 'assistant')):.2f}s
            """)
        
        # 도움말
        st.divider()
        st.subheader("❓ 도움말")
        with st.expander("사용 방법"):
            st.markdown("""
            1. 질문 입력
            2. 제출 버튼 클릭
            3. 답변 및 출처 확인
            """)
        
        with st.expander("예시 질문"):
            for q in EXAMPLE_QUESTIONS[:4]:
                if st.button(f"💬 {q}", use_container_width=True, key=f"example_{q}"):
                    st.session_state.user_input = q
                    st.rerun()


# ==================== 통계 표시 ====================

def display_statistics():
    """대화 통계 표시"""
    if not st.session_state.chat_history:
        st.info("📊 아직 통계 데이터가 없습니다.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 질문 수
    num_questions = sum(1 for msg in st.session_state.chat_history if msg['role'] == 'user')
    with col1:
        st.metric("❓ 총 질문 수", num_questions)
    
    # 평균 응답 시간
    response_times = [msg.get('elapsed_time', 0) for msg in st.session_state.chat_history 
                     if msg['role'] == 'assistant']
    avg_time = sum(response_times) / len(response_times) if response_times else 0
    with col2:
        st.metric("⏱️ 평균 응답 시간", f"{avg_time:.2f}초")
    
    # 웹 검색 사용 횟수
    web_search_count = sum(1 for msg in st.session_state.chat_history 
                          if msg['role'] == 'assistant' 
                          and msg.get('debug_info', {}).get('web_search_needed') == 'Yes')
    with col3:
        st.metric("🌐 웹 검색 사용", web_search_count)
    
    # 총 응답 시간
    total_time = sum(response_times)
    with col4:
        st.metric("⏲️ 총 응답 시간", f"{total_time:.1f}초")
    
    # 응답 시간 그래프
    st.subheader("📈 응답 시간 추이")
    if response_times:
        import streamlit.components.v1 as components
        st.line_chart(response_times)


# ==================== 메인 앱 ====================

def main():
    """메인 애플리케이션"""
    initialize_session_state()
    render_sidebar()
    
    # 헤더
    st.title("🏥 의료 RAG 챗봇 (고급 버전)")
    st.markdown("""
    **LangGraph CRAG 기반 고급 RAG 시스템**
    
    설정 프리셋, 성능 모니터링, 고급 커스터마이징을 지원합니다.
    """)
    
    # RAG 파이프라인 초기화
    if st.session_state.pipeline is None:
        st.session_state.pipeline = initialize_rag_pipeline(st.session_state.rag_config)
    
    # 대화 영역
    st.subheader("💬 대화")
    display_chat_history()
    
    st.divider()
    
    # 입력 영역
    st.subheader("📝 질문 입력")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "질문을 입력하세요:",
            key="user_input",
            placeholder=st.session_state.ui_config.placeholder_text,
            label_visibility="collapsed"
        )
    
    with col2:
        st.button("📤 제출", use_container_width=True, on_click=handle_question_submission)
    
    # 통계 표시
    if st.session_state.show_stats:
        st.divider()
        st.subheader("📊 대화 통계")
        display_statistics()


if __name__ == "__main__":
    main()

