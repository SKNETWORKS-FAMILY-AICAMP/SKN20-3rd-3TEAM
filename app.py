"""
Streamlit 기반 RAG 웹 애플리케이션
LangGraph CRAG 파이프라인을 Streamlit UI와 통합

사용법:
  streamlit run app.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

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

# 로거 설정
logger = get_logger(__name__)

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="🏥 의료 RAG 챗봇",
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
    
    .chat-timestamp {
        font-size: 0.8em;
        color: #999;
        margin-top: 4px;
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
    
    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        height: 40px;
        font-size: 1em;
        border-radius: 8px;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background-color: #F9F9F9;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin: 10px 0;
    }
    
    /* 에러 메시지 */
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #C62828;
    }
    
    /* 로딩 상태 */
    .loading-indicator {
        text-align: center;
        color: #1976D2;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 초기화 함수 ====================

@st.cache_resource
def initialize_rag_pipeline():
    """
    RAG 파이프라인 초기화 (Streamlit 캐시 사용)
    
    Returns:
        RAG 파이프라인 객체
    """
    try:
        with st.spinner("🔄 RAG 시스템 초기화 중..."):
            # 1. 임베딩 모델 로드
            embedding_model = get_embedding_model("openai")
            
            # 2. 벡터스토어 로드
            vectorstore = load_vectorstore(
                embedding_model,
                persist_directory="./chroma_db",
                collection_name="rag_collection"
            )
            
            # 3. Retriever 생성
            retriever = create_retriever(
                vectorstore,
                top_k=5
            )
            
            # 4. LangGraph CRAG 파이프라인 생성 (디버그 로그 비활성화)
            pipeline = LangGraphRAGPipeline(
                retriever,
                llm_model="gpt-4o-mini",
                temperature=0.0,
                debug=False  # Streamlit 환경에서는 디버그 로그 비활성화
            )
            
        st.success("✅ RAG 시스템 준비 완료!")
        return pipeline
    
    except Exception as e:
        st.error(f"❌ RAG 시스템 초기화 실패: {str(e)}")
        logger.error(f"RAG initialization error: {str(e)}")
        return None


def initialize_session_state():
    """
    Streamlit 세션 상태 초기화
    """
    # 대화 기록
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # RAG 파이프라인
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    
    # UI 상태
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    
    if "show_debug_info" not in st.session_state:
        st.session_state.show_debug_info = False


# ==================== 채팅 표시 함수 ====================

def display_chat_message(role: str, content: str, timestamp: str = None, sources: List[Dict] = None):
    """
    채팅 메시지를 화면에 표시
    
    Args:
        role: "user" 또는 "assistant"
        content: 메시지 내용
        timestamp: 메시지 타임스탬프 (선택사항)
        sources: 답변의 출처 정보 (assistant일 때만)
    """
    if role == "user":
        st.markdown(f"""
        <div class="chat-user">
            <strong>👤 당신:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    
    elif role == "assistant":
        st.markdown(f"""
        <div class="chat-assistant">
            <strong>🤖 AI 어시스턴트:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
        
        # 출처 정보 표시
        if sources and len(sources) > 0:
            with st.expander(f"📚 참고한 문서 ({len(sources)}개)"):
                for i, source in enumerate(sources, 1):
                    col1, col2 = st.columns([1, 3])
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
    """
    저장된 대화 기록 표시
    """
    if not st.session_state.chat_history:
        st.info("💬 아직 대화가 없습니다. 질문을 입력해주세요!")
        return
    
    for message in st.session_state.chat_history:
        role = message.get("role")
        content = message.get("content")
        timestamp = message.get("timestamp")
        sources = message.get("sources", [])
        
        display_chat_message(role, content, timestamp, sources)


# ==================== 질문 처리 함수 ====================

def process_question(question: str, pipeline: LangGraphRAGPipeline) -> Dict[str, Any]:
    """
    질문을 처리하고 답변 생성
    
    Args:
        question: 사용자 질문
        pipeline: RAG 파이프라인
        
    Returns:
        답변 및 메타데이터 딕셔너리
    """
    try:
        with st.spinner("🔄 답변을 생성 중입니다..."):
            start_time = time.time()
            result = pipeline.rag_pipeline_with_sources(question)
            elapsed_time = time.time() - start_time
            
            result['elapsed_time'] = elapsed_time
            return result
    
    except Exception as e:
        logger.error(f"Question processing error: {str(e)}")
        return {
            'answer': f"❌ 오류 발생: {str(e)}",
            'sources': [],
            'elapsed_time': 0
        }


def handle_question_submission():
    """
    질문 제출 핸들러
    """
    question = st.session_state.user_input.strip()
    
    if not question:
        st.warning("⚠️ 질문을 입력해주세요!")
        return
    
    # 파이프라인 초기화 확인
    if st.session_state.pipeline is None:
        st.error("❌ RAG 시스템이 준비되지 않았습니다.")
        return
    
    # 대화 기록에 사용자 질문 추가
    st.session_state.chat_history.append({
        "role": "user",
        "content": question,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # 질문 처리
    result = process_question(question, st.session_state.pipeline)
    
    # 대화 기록에 AI 답변 추가
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
    
    # 입력 필드 초기화
    st.session_state.user_input = ""


# ==================== 사이드바 설정 ====================

def render_sidebar():
    """
    사이드바 렌더링
    """
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 시스템 정보
        st.subheader("🔧 시스템 상태")
        if st.session_state.pipeline:
            st.success("✅ RAG 시스템 준비됨")
        else:
            st.error("❌ RAG 시스템 준비 중...")
        
        # 표시 옵션
        st.subheader("📋 표시 옵션")
        st.session_state.show_sources = st.checkbox(
            "출처 정보 표시",
            value=st.session_state.show_sources
        )
        st.session_state.show_debug_info = st.checkbox(
            "디버그 정보 표시",
            value=st.session_state.show_debug_info
        )
        
        # 대화 관리
        st.subheader("💬 대화 관리")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 대화 초기화", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("📊 통계", use_container_width=True):
                st.session_state.show_stats = True
        
        # 도움말
        st.subheader("❓ 도움말")
        st.markdown("""
        ### 사용 방법
        1. **질문 입력**: 아래 텍스트 상자에 질문을 입력하세요
        2. **제출**: '질문 제출' 버튼을 클릭하세요
        3. **답변 확인**: AI의 답변과 참고 문서를 확인하세요
        
        ### 팁
        - 구체적이고 명확한 질문이 더 정확한 답변을 생성합니다
        - 의료 관련 질문에 최적화되어 있습니다
        - 내부 문서에 없는 정보는 웹 검색으로 자동 보완됩니다
        """)
        
        # 예시 질문
        st.subheader("💡 예시 질문")
        example_questions = [
            "강아지 피부 질환의 증상은 무엇인가요?",
            "벼룩 알러지성 피부염 치료법을 알려주세요",
            "개의 혈액형에 대해 설명해주세요",
            "면역 체계 질환의 종류는?",
        ]
        
        for example in example_questions:
            if st.button(f"💬 {example}", use_container_width=True, key=f"example_{example}"):
                st.session_state.user_input = example
                st.rerun()


# ==================== 통계 표시 ====================

def display_statistics():
    """
    대화 통계 표시
    """
    if not st.session_state.chat_history:
        st.info("📊 아직 통계 데이터가 없습니다.")
        return
    
    col1, col2, col3 = st.columns(3)
    
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
        st.metric("🌐 웹 검색 사용 횟수", web_search_count)


# ==================== 디버그 정보 표시 ====================

def display_debug_info(message: Dict):
    """
    메시지의 디버그 정보 표시
    
    Args:
        message: 대화 메시지
    """
    if message['role'] != 'assistant':
        return
    
    debug_info = message.get('debug_info', {})
    
    with st.expander("🐛 디버그 정보"):
        col1, col2, col3 = st.columns(3)
        
        # 문서 유사도 점수
        with col1:
            doc_scores = debug_info.get('document_scores', [])
            if doc_scores:
                st.markdown("**📊 Similarity Scores:**")
                for i, score in enumerate(doc_scores[:5], 1):
                    st.markdown(f"  {i}. {score:.4f}")
        
        # 관련성 판정 결과
        with col2:
            grade_results = debug_info.get('grade_results', [])
            if grade_results:
                yes_count = sum(1 for g in grade_results if g == 'YES')
                no_count = sum(1 for g in grade_results if g == 'NO')
                st.markdown("**✓ 관련성 판정:**")
                st.markdown(f"  관련있음: {yes_count}개")
                st.markdown(f"  관련없음: {no_count}개")
        
        # 웹 검색 여부
        with col3:
            web_search_needed = debug_info.get('web_search_needed', 'No')
            st.markdown("**🌐 웹 검색:**")
            if web_search_needed == 'Yes':
                st.markdown("  ✓ 실행됨")
            else:
                st.markdown("  ✗ 미실행")


# ==================== 메인 앱 ====================

def main():
    """
    메인 애플리케이션 함수
    """
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 헤더
    st.title("🏥 의료 RAG 챗봇")
    st.markdown("""
    **Retrieval-Augmented Generation (RAG) 기반 의료 QA 시스템**
    
    이 애플리케이션은 동물 의료 관련 질문에 대해 내부 문서와 웹 검색을 활용한 
    정확한 답변을 제공합니다.
    """)
    
    # RAG 파이프라인 초기화
    if st.session_state.pipeline is None:
        st.session_state.pipeline = initialize_rag_pipeline()
    
    # 대화 영역
    st.subheader("💬 대화")
    
    # 대화 기록 표시
    display_chat_history()
    
    # 구분선
    st.divider()
    
    # 입력 영역
    st.subheader("📝 질문 입력")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "질문을 입력하세요:",
            key="user_input",
            placeholder="예: 강아지 피부 질환의 증상은 무엇인가요?",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.button(
            "📤 제출",
            use_container_width=True,
            on_click=handle_question_submission
        )
    
    # 디버그 정보 표시 (마지막 메시지)
    if st.session_state.show_debug_info and st.session_state.chat_history:
        last_message = st.session_state.chat_history[-1]
        if last_message['role'] == 'assistant':
            display_debug_info(last_message)
    
    # 통계 표시 (세션 상태에 플래그가 있을 때)
    if st.session_state.get('show_stats', False):
        st.divider()
        st.subheader("📊 대화 통계")
        display_statistics()
        st.session_state.show_stats = False


if __name__ == "__main__":
    main()

