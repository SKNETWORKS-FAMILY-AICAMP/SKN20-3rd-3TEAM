import os
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from dotenv import load_dotenv

# prompt_new.py에서 필요한 함수들 import
from prompt_new import (
    initialize_rag_system,
    get_rag_prompt,
    get_rewrite_prompt,
    format_docs,
    filter_docs_by_response
)

from langchain_core.output_parsers import StrOutputParser

# ---------------------------
# 환경 설정
# ---------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")

VECTORSTORE_PATH = r"..\data\ChromaDB_bge_m3"
COLLECTION_NAME = "pet_health_qa_system_bge_m3"

st.set_page_config(
    page_title="반려견 질병 Q&A",
    page_icon="🐶",
    layout="wide",
)


# ---------------------------
# 세션 상태 초기화
# ---------------------------
@st.cache_resource
def load_rag_system():
    """RAG 시스템 한 번만 로드"""
    return initialize_rag_system(
        vectorstore_path=VECTORSTORE_PATH,
        collection_name=COLLECTION_NAME
    )


# RAG 시스템 로드
rag_system = load_rag_system()

if "retriever" not in st.session_state:
    st.session_state.retriever = rag_system['retriever']
    st.session_state.llm = rag_system['llm']
    st.session_state.rag_prompt = get_rag_prompt()
    st.session_state.rewrite_prompt = get_rewrite_prompt()

if "submit_count" not in st.session_state:
    st.session_state.submit_count = 0

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "message_docs" not in st.session_state:
    st.session_state.message_docs = {}


# ---------------------------
# 채팅 페이지
# ---------------------------
def show_chat():
    """채팅 스타일의 Q&A 인터페이스"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 10px;">
        <h1 style="font-size: 60px; font-weight: 900; color: #1e40af; margin: 0; line-height: 1.2;">
            반려견 건강 상담 ChatBot
        </h1>
        <p style="font-size: 14px; color: #666; margin: 8px 0 0 0;">
            궁금한 반려견 건강 증상에 대해 물어보세요. 신뢰할 수 있는 의료 자료를 바탕으로 정확한 답변을 드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2열 레이아웃: 왼쪽(문서) - 오른쪽(채팅)
    col_docs, col_chat = st.columns([1, 2], gap="large")
    
    with col_chat:
        st.markdown("### 💬 대화")
        
        # 채팅 메시지 표시
        for idx, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "user":
                # 사용자 메시지 (오른쪽, 노란색)
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">
                        <div style="background-color: #FFF9E6; padding: 14px 18px; border-radius: 16px; max-width: 80%; word-wrap: break-word;">
                            <span style="color: #333; font-size: 15px; line-height: 1.5;">{message['content']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # AI 메시지 (왼쪽, 흰색)
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
                        <div style="background-color: #F0F4F8; padding: 14px 18px; border-radius: 16px; max-width: 80%; word-wrap: break-word;">
                            <strong style="color: #1e40af; font-size: 13px;">🐶 수의사 AI</strong><br>
                            <span style="color: #333; font-size: 14px; line-height: 1.6; margin-top: 6px; display: block;">{message['content']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # 입력 폼
        st.markdown("---")
        with st.form(key=f"chat_form_{st.session_state.submit_count}", border=True):
            col1, col2 = st.columns([5, 1], gap="small")
            with col1:
                user_input = st.text_input(
                    label="",
                    placeholder="🐕 강아지의 증상이나 질문을 입력하세요...",
                    label_visibility="collapsed"
                )
            with col2:
                submitted = st.form_submit_button("➤ 전송", use_container_width=True)
        
        # 메시지 처리
        if submitted and user_input.strip():
            # 사용자 메시지 추가
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input.strip()
            })
            
            with st.spinner("답변을 준비 중입니다..."):
                try:
                    # 1. 질문 변환 (rewrite chain)
                    rewrite_chain = st.session_state.rewrite_prompt | st.session_state.llm | StrOutputParser()
                    transformed_query = rewrite_chain.invoke({"question": user_input.strip()})
                    
                    # 2. 벡터스토어에서 문서 검색
                    docs = st.session_state.retriever.invoke(transformed_query)
                    
                    if not docs:
                        ai_response = "죄송합니다. 관련된 정보를 찾을 수 없습니다. 더 구체적으로 설명해주시겠어요?"
                        docs_to_save = []
                    else:
                        # 3. 문서 포맷팅
                        context = format_docs(docs)
                        
                        # 4. RAG 체인 실행
                        rag_chain = st.session_state.rag_prompt | st.session_state.llm | StrOutputParser()
                        ai_response = rag_chain.invoke({"context": context, "question": transformed_query})
                        
                        # 5. 응답에 실제로 사용된 문서만 필터링
                        docs_to_save = filter_docs_by_response(docs, ai_response)
                    
                    # AI 응답 추가
                    message_idx = len(st.session_state.chat_messages)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    # 해당 메시지의 문서 저장 (문서가 있을 때만)
                    if docs_to_save:
                        st.session_state.message_docs[message_idx] = docs_to_save
                    
                    # submit_count 증가하여 form key 변경 -> 입력창 초기화
                    st.session_state.submit_count += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
        
        # 초기화 버튼
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.message_docs = {}
            st.rerun()
    
    # 왼쪽 열: 참고 문서 표시
    with col_docs:
        st.markdown("### 📚 참고 문서")
        
        # 최근 AI 응답의 문서 찾기
        last_ai_message_idx = None
        for i in range(len(st.session_state.chat_messages) - 1, -1, -1):
            if st.session_state.chat_messages[i]["role"] == "assistant":
                last_ai_message_idx = i
                break
        
        if last_ai_message_idx is not None and last_ai_message_idx in st.session_state.message_docs:
            docs = st.session_state.message_docs[last_ai_message_idx]
            for doc_idx, doc in enumerate(docs, 1):
                metadata = doc.metadata
                
                # 문서 유형에 따른 출처 정보
                if metadata.get("source_type") == "qa_data":
                    source_info = f"📋 상담기록\n{metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
                else:
                    source_info = f"📖 서적\n{metadata.get('title', '')}"
                    if metadata.get('author'):
                        source_info += f"\n저자: {metadata['author']}"
                    if metadata.get('page'):
                        source_info += f"\np.{metadata['page']+1}"
                
                with st.expander(f"문서 {doc_idx}", expanded=False):
                    st.markdown(f"**출처 정보**\n{source_info}")
                    st.markdown("---")
                    st.markdown(f"**내용**\n{doc.page_content[:200]}...")
        else:
            st.info("질문을 입력하면 참고한 문서가 표시됩니다.")


# 채팅 페이지 실행
show_chat()
