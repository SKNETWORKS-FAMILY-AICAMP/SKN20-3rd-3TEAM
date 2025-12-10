"""
Streamlit 챗봇 인터페이스
반려견 건강 상담 AI 어시스턴트
"""

import os
import sys
import streamlit as st
import pickle
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pipeline import RAGPipeline


# 페이지 설정
st.set_page_config(
    page_title="반려견 건강 상담 AI",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 세션 스테이트 초기화
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'pipeline_ready' not in st.session_state:
    st.session_state.pipeline_ready = False


def initialize_pipeline(force_rebuild: bool = False):
    """RAG 파이프라인 초기화"""
    try:
        with st.spinner('🔄 AI 시스템 초기화 중... (최초 실행시 1-2분 소요)'):
            pipeline = RAGPipeline(
                project_root=str(project_root),
                use_cache=True
            )
            pipeline.setup(force_rebuild=force_rebuild)
            st.session_state.pipeline = pipeline
            st.session_state.pipeline_ready = True
            st.success('✅ AI 시스템 준비 완료!')
    except Exception as e:
        st.error(f'❌ 초기화 실패: {str(e)}')
        st.session_state.pipeline_ready = False


def main():
    """메인 UI"""
    
    # 헤더
    st.title("🐕 반려견 건강 상담 AI")
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 시스템 상태
        if st.session_state.pipeline_ready:
            st.success("✅ 시스템 활성화")
        else:
            st.warning("⚠️ 시스템 초기화 필요")
        
        st.markdown("---")
        
        # 초기화 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 시작하기", use_container_width=True):
                initialize_pipeline(force_rebuild=False)
        
        with col2:
            if st.button("🔄 재구성", use_container_width=True):
                st.session_state.pipeline_ready = False
                st.session_state.pipeline = None
                st.session_state.chat_history = []
                initialize_pipeline(force_rebuild=True)
        
        st.markdown("---")
        
        # 검색 설정
        st.subheader("🔍 검색 설정")
        use_rewrite = st.checkbox("쿼리 재작성 사용", value=True, 
                                   help="검색 쿼리를 AI가 최적화합니다")
        
        show_sources = st.checkbox("출처 표시", value=True,
                                    help="응답과 함께 참고 문서를 표시합니다")
        
        st.markdown("---")
        
        # 대화 기록 관리
        st.subheader("💬 대화 관리")
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.caption(f"현재 대화: {len(st.session_state.chat_history)}개")
        
        st.markdown("---")
        
        # 정보
        st.subheader("ℹ️ 사용 방법")
        st.markdown("""
        1. **시작하기** 버튼으로 AI 초기화
        2. 반려견의 증상이나 궁금한 점을 입력
        3. AI가 수의학 자료를 기반으로 답변
        
        **주의사항**
        - 응급 상황시 즉시 동물병원 방문
        - AI 답변은 참고용이며 진단이 아닙니다
        """)
    
    # 메인 컨텐츠
    if not st.session_state.pipeline_ready:
        st.info("👈 왼쪽 사이드바에서 **시작하기** 버튼을 눌러주세요!")
        
        # 예시 질문 표시
        st.subheader("💡 예시 질문")
        example_questions = [
            "강아지가 계속 구토를 해요. 원인이 뭘까요?",
            "강아지가 발을 절뚝거려요. 어떻게 해야 하나요?",
            "강아지 눈에서 눈곱이 많이 나와요.",
            "강아지가 밥을 안 먹어요. 괜찮을까요?",
            "강아지 피부에 붉은 반점이 생겼어요."
        ]
        
        for q in example_questions:
            st.markdown(f"- {q}")
        
        return
    
    # 채팅 UI
    st.subheader("💬 상담 시작")
    
    # 대화 기록 표시
    for user_msg, bot_msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(user_msg)
        
        with st.chat_message("assistant", avatar="🐕"):
            st.write(bot_msg)
    
    # 입력창
    user_input = st.chat_input("반려견의 증상이나 궁금한 점을 입력하세요...")
    
    if user_input:
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)
        
        # AI 응답 생성
        with st.chat_message("assistant", avatar="🐕"):
            with st.spinner("답변 생성 중..."):
                try:
                    # 파이프라인 쿼리
                    response, sources = st.session_state.pipeline.query(
                        question=user_input,
                        use_rewrite=use_rewrite,
                        return_sources=show_sources
                    )
                    
                    # 응답 표시
                    st.write(response)
                    
                    # 출처 표시 (옵션)
                    if show_sources and sources:
                        with st.expander("📚 참고 문서 보기"):
                            for i, doc in enumerate(sources, 1):
                                source_type = doc.metadata.get('source_type', 'unknown')
                                
                                st.markdown(f"**[문서 {i}]** ({source_type})")
                                
                                if source_type == 'qa_data':
                                    st.caption(
                                        f"생애주기: {doc.metadata.get('life_stage', 'N/A')} | "
                                        f"과: {doc.metadata.get('department', 'N/A')} | "
                                        f"질병: {doc.metadata.get('disease', 'N/A')}"
                                    )
                                elif source_type == 'medical_data':
                                    st.caption(
                                        f"책: {doc.metadata.get('book_title', 'N/A')} | "
                                        f"저자: {doc.metadata.get('author', 'N/A')} | "
                                        f"출판사: {doc.metadata.get('publisher', 'N/A')}"
                                    )
                                
                                st.text(doc.page_content[:200] + "...")
                                st.markdown("---")
                    
                    # 대화 기록 저장
                    st.session_state.chat_history.append((user_input, response))
                    
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
