"""
Streamlit 기본 RAG 웹 애플리케이션
==================================
공통 모듈을 사용한 기본 RAG 채팅 앱

실행: streamlit run app.py
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# 공통 모듈 import
from common.utils import setup_logging
from common.config import CommonConfig, get_config
from common.extensions.embeddings import OpenAIEmbeddingModel
from common.extensions.vectorstores import ChromaVectorStore
from common.extensions.retrievers import SimpleTopKRetriever
from common.extensions.llm_clients import OpenAILLMClient
from common.pipelines import SimpleRAGPipeline

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = setup_logging()

# ============ Streamlit 페이지 설정 ============
st.set_page_config(
    page_title="🏥 의료 RAG 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .source-box {
        background-color: #fffde7;
        border-left: 4px solid #FBC02D;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }
    .metric-box {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============ 세션 상태 초기화 ============
def initialize_session_state():
    """세션 상태 초기화"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    
    if "config" not in st.session_state:
        st.session_state.config = CommonConfig()
    
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    
    if "show_debug_info" not in st.session_state:
        st.session_state.show_debug_info = False
    
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "total_time": 0.0,
        }


initialize_session_state()


# ============ RAG 파이프라인 초기화 ============
@st.cache_resource
def initialize_pipeline():
    """RAG 파이프라인 초기화 (캐시됨)"""
    try:
        with st.spinner("🔄 RAG 시스템 초기화 중..."):
            logger.info("RAG 시스템 초기화 시작")
            
            # 임베딩 모델 초기화
            st.status("📚 임베딩 모델 로드 중...", state="running")
            embedding = OpenAIEmbeddingModel(
                model_name="text-embedding-3-small"
            )
            st.status("📚 임베딩 모델 완료", state="complete")
            
            # 벡터 저장소 초기화
            st.status("💾 벡터 저장소 로드 중...", state="running")
            vectorstore = ChromaVectorStore(
                embedding_model=embedding,
                persist_directory="./chroma_db",
                collection_name="medical_documents"
            )
            st.status("💾 벡터 저장소 완료", state="complete")
            
            # 검색기 초기화
            st.status("🔍 검색기 초기화 중...", state="running")
            retriever = SimpleTopKRetriever(
                vector_store=vectorstore,
                top_k=5
            )
            st.status("🔍 검색기 완료", state="complete")
            
            # LLM 클라이언트 초기화
            st.status("🤖 LLM 클라이언트 초기화 중...", state="running")
            llm_client = OpenAILLMClient(
                model_name="gpt-4o-mini",
                temperature=0.7
            )
            st.status("🤖 LLM 완료", state="complete")
            
            # 파이프라인 생성
            st.status("⚙️ 파이프라인 구성 중...", state="running")
            pipeline = SimpleRAGPipeline(
                retriever=retriever,
                embedding_model=embedding,
                vector_store=vectorstore,
                llm_client=llm_client,
                config=st.session_state.config.pipeline,
            )
            st.status("⚙️ 파이프라인 완료", state="complete")
            
            logger.info("✅ RAG 시스템 초기화 완료")
            st.success("✅ RAG 시스템 준비 완료!")
            
            return pipeline
    
    except Exception as e:
        logger.error(f"❌ 초기화 오류: {e}")
        st.error(f"❌ 초기화 실패: {e}")
        return None


# ============ 메시지 표시 함수 ============
def display_chat_message(role: str, content: str, sources: list = None, elapsed_time: float = None):
    """채팅 메시지 표시"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div style="flex: 1;">
                <strong>👤 You</strong>
                <p>{content}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:  # assistant
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div style="flex: 1;">
                <strong>🤖 AI Assistant</strong>
                <p>{content}</p>
                {f'<small>⏱️ {elapsed_time:.2f}s</small>' if elapsed_time else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 출처 표시
        if sources and st.session_state.show_sources:
            with st.expander(f"📚 참고한 문서 ({len(sources)}개)"):
                for i, source in enumerate(sources, 1):
                    st.markdown(f"""
                    **[{i}] {source.get('title', 'Unknown')}**
                    - 유사도: {source.get('similarity_score', 0):.2%}
                    """)


# ============ 질문 처리 함수 ============
def process_question(question: str):
    """사용자 질문 처리"""
    if not question.strip():
        st.warning("⚠️ 질문을 입력해주세요")
        return
    
    if st.session_state.pipeline is None:
        st.error("❌ 파이프라인이 초기화되지 않았습니다")
        return
    
    try:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().isoformat(),
        })
        
        # 답변 생성
        with st.spinner("🔄 답변을 생성 중입니다..."):
            logger.info(f"질문 처리: {question}")
            
            response = st.session_state.pipeline.process(
                question,
                top_k=5,
            )
            
            # 응답 정보 추출
            answer = response['answer']
            sources = response['sources']
            elapsed_time = float(response['metrics']['total_time'].rstrip('s'))
            
            # AI 메시지 추가
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "elapsed_time": elapsed_time,
                "timestamp": datetime.now().isoformat(),
                "debug_info": response.get('debug_info', {}),
            })
            
            # 통계 업데이트
            st.session_state.stats["total_queries"] += 1
            st.session_state.stats["successful_queries"] += 1
            st.session_state.stats["total_time"] += elapsed_time
            
            logger.info(f"✅ 답변 생성 완료 ({elapsed_time:.2f}초)")
        
        # 화면 갱신
        st.rerun()
    
    except Exception as e:
        logger.error(f"❌ 질문 처리 오류: {e}")
        st.error(f"❌ 오류 발생: {e}")


# ============ 사이드바 설정 ============
def render_sidebar():
    """사이드바 UI 구성"""
    with st.sidebar:
        st.title("⚙️ 설정")
        
        # 시스템 상태
        st.subheader("📊 시스템 상태")
        if st.session_state.pipeline:
            st.success("✅ RAG 시스템 준비됨")
        else:
            st.error("❌ RAG 시스템 미준비")
        
        st.divider()
        
        # 표시 옵션
        st.subheader("👁️ 표시 옵션")
        st.session_state.show_sources = st.checkbox(
            "출처 표시",
            value=st.session_state.show_sources,
        )
        st.session_state.show_debug_info = st.checkbox(
            "디버그 정보 표시",
            value=st.session_state.show_debug_info,
        )
        
        st.divider()
        
        # 대화 관리
        st.subheader("💬 대화 관리")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 새로고침"):
                st.rerun()
        
        with col2:
            if st.button("🗑️ 초기화"):
                st.session_state.chat_history = []
                st.session_state.stats = {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "total_time": 0.0,
                }
                st.success("✅ 초기화 완료")
                st.rerun()
        
        st.divider()
        
        # 통계
        st.subheader("📈 대화 통계")
        stats = st.session_state.stats
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <h3>{stats['total_queries']}</h3>
                <p>총 질문</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            success_rate = (
                stats['successful_queries'] / max(1, stats['total_queries']) * 100
            )
            st.markdown(f"""
            <div class="metric-box">
                <h3>{success_rate:.0f}%</h3>
                <p>성공률</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_time = (
                stats['total_time'] / max(1, stats['total_queries'])
            )
            st.markdown(f"""
            <div class="metric-box">
                <h3>{avg_time:.2f}s</h3>
                <p>평균 시간</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # 도움말
        st.subheader("❓ 도움말")
        st.info("""
        **사용 방법:**
        1. 질문을 입력하세요
        2. 📤 제출 버튼을 클릭
        3. AI의 답변을 확인
        4. 출처 정보 확인
        
        **팁:**
        - 구체적인 질문이 더 좋은 답변을 생성합니다
        - 출처를 확인하여 정보의 신뢰성을 검증하세요
        """)


# ============ 메인 UI ============
def main():
    """메인 페이지"""
    
    # 헤더
    st.title("🏥 의료 RAG 챗봇")
    st.markdown("**공통 모듈 기반 RAG 시스템**")
    st.divider()
    
    # 사이드바
    render_sidebar()
    
    # 파이프라인 초기화
    st.session_state.pipeline = initialize_pipeline()
    
    # 대화 표시
    st.subheader("💬 대화")
    
    # 채팅 기록 표시
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                display_chat_message(
                    "user",
                    message["content"]
                )
            else:
                display_chat_message(
                    "assistant",
                    message["content"],
                    sources=message.get("sources", []),
                    elapsed_time=message.get("elapsed_time"),
                )
                
                # 디버그 정보 표시 (선택사항)
                if st.session_state.show_debug_info and message.get("debug_info"):
                    with st.expander("🐛 디버그 정보"):
                        debug_info = message["debug_info"]
                        st.json(debug_info)
    else:
        st.info("💡 질문을 입력하여 시작하세요!")
    
    st.divider()
    
    # 질문 입력
    st.subheader("📝 질문 입력")
    
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        question = st.text_input(
            "질문을 입력하세요:",
            placeholder="예: 강아지 피부 질환의 증상은 무엇인가요?",
            label_visibility="collapsed",
        )
    
    with col2:
        if st.button("📤 제출", use_container_width=True):
            if question.strip():
                process_question(question)
            else:
                st.warning("질문을 입력해주세요")


# ============ 애플리케이션 실행 ============
if __name__ == "__main__":
    main()
