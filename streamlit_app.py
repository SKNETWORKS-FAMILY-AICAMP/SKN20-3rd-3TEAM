import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from src.ensemble import EnsembleRetriever

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ---------------------------
# 환경 설정 & 전역 객체
# ---------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")

# 설정값 정의
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0
RETRIEVER_K = 5
VECTORSTORE_PATH = r".\data\ChromaDB_bge_m3"  # prompt_new.py와 동일한 경로
COLLECTION_NAME = "pet_health_qa_system_bge_m3"

st.set_page_config(
    page_title="반려견 질병 Q&A",
    page_icon="🐶",
    layout="wide",
)

# ---------------------------
# Retriever 생성
# ---------------------------
def get_retriever(k=RETRIEVER_K):
    """벡터스토어로부터 리트리버 생성 (유사도 + BM25 앙상블)"""
    # BGE-M3 임베딩 모델 로드 (prompt_new.py와 동일)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},  # GPU 사용시 'cuda'로 변경
        encode_kwargs={'normalize_embeddings': True}  # bge-m3는 정규화 권장
    )
    
    # 벡터스토어 로드 (prompt_new.py와 동일)
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    print("벡터스토어가 성공적으로 로드되었습니다!")
    
    # 컬렉션 확인
    client = chromadb.PersistentClient(path=VECTORSTORE_PATH)
    collections = client.list_collections()
    print("사용 가능한 컬렉션:", [c.name for c in collections])
    
    # 기본 리트리버
    retriever = vectorstore.as_retriever(search_kwargs={"k": k}, search_type="similarity")
    
    # BM25 리트리버 생성
    collection = vectorstore._collection
    doc_count = collection.count()
    
    if doc_count == 0:
        raise ValueError("벡터스토어가 비어있습니다. 먼저 문서를 추가해주세요.")
    
    # ChromaDB에서 모든 문서 가져오기
    all_data = collection.get(limit=doc_count)
    
    # Document 객체로 변환
    bm25_docs = []
    if all_data and 'ids' in all_data and len(all_data['ids']) > 0:
        documents = all_data.get('documents', [])
        metadatas = all_data.get('metadatas', [])
        
        for i, doc_id in enumerate(all_data['ids']):
            page_content = documents[i] if i < len(documents) else ""
            metadata = metadatas[i] if i < len(metadatas) else {}
            bm25_docs.append(Document(page_content=page_content, metadata=metadata))
    
    if len(bm25_docs) == 0:
        raise ValueError("벡터스토어에서 문서를 가져올 수 없습니다.")
    
    print(f"BM25 리트리버용 문서 {len(bm25_docs)}개 로드 완료")
    retriever_bm25 = BM25Retriever.from_documents(bm25_docs)
    
    # 앙상블 리트리버
    retriever_ensemble = EnsembleRetriever(
        retrievers=[retriever, retriever_bm25],
        weights=[0.5, 0.5]  # 가중치 합은 1이어야 합니다.
    )
    
    return retriever_ensemble

# 세션 상태 초기화
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "retriever" not in st.session_state:
    st.session_state.retriever = get_retriever(k=RETRIEVER_K)

if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        openai_api_key=OPENAI_API_KEY,
    )

# RAG 프롬프트 정의 (prompt_new.py 기반)
if "rag_prompt" not in st.session_state:
    st.session_state.rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
문맥에 없는 정보는 절대로 추측하거나 생성하지 마세요.

[사용 가능한 정보 유형]
- medical_data: 수의학 서적 또는 논문
- qa_data: 보호자-수의사 상담 기록 (생애주기 / 과 / 질병 태그 포함)

[할루시네이션 방지 규칙]
1. 문맥에 없는 정보는 사용하지 마세요.
2. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."라고 답변하세요.
3. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
4. **질문에 합당한 답변만 제공하세요. 거짓 정보나 불필요한 정보는 제외하세요.**

[응답 규칙]
- 보호자가 작성한 반려견 상태를 2~3문장으로 요약한다.
- 문맥에서 확인된 가능한 원인을 구체적으로 설명한다. 
  (문맥에 없다면 "문서에 해당 정보가 없습니다"라고 쓴다)
- 집에서 가능한 안전한 관리 방법 2~3개 제안한다. 
  (문맥에 없다면 제안하지 않는다)
- 언제 병원에 가야 하는지, 어떤 증상이 응급인지 문서 기반으로 설명한다.
- 마지막 줄에 반드시 대답 생성에 사용한 모든 문서의 출처를 명시한다:
  • 서적 출처: 책 제목 / 저자 / 출판사
  • QA 출처: 생애주기 / 과 / 질병

[전체 톤]
- 공손한 존댓말
- 보호자를 안심시키되, 필요한 부분은 명확하게 안내하는 수의사 상담 톤

[출력 형식]
-상태 요약:
-가능한 원인:
-집에서 관리 방법:
-병원 방문 시기:

"""),
        ("human", """
문맥: {context}

사용자 질문: {question}
""")
    ])

# 질문 변환 프롬프트 (prompt_new.py 기반)
if "rewrite_prompt" not in st.session_state:
    st.session_state.rewrite_prompt = PromptTemplate.from_template(
        """다음 질문을 검색에 더 적합한 형태로 변환해 주세요.
키워드 중심으로 명확하게 바꿔주세요.
변환된 검색어만 출력하세요.

원본 질문: {question}
변환된 검색어:""")

if "selected_qa_index" not in st.session_state:
    st.session_state.selected_qa_index = None

if "page" not in st.session_state:
    st.session_state.page = "home"  # "home", "qa", or "chat"

if "popular_qa" not in st.session_state:
    st.session_state.popular_qa = []

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ---------------------------
# 문서 포맷팅 함수 (prompt.py 기반)
# ---------------------------
def format_docs(docs):
    """문서를 출처 정보와 함께 포맷팅"""
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata
        
        # 데이터 유형에 따라 출처 정보 구성
        if metadata.get("source_type") == "qa_data":
            source_info = f"상담기록 - {metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
        else:
            source_info = f"서적 - {metadata.get('title', '')}"
            if metadata.get('author'):
                source_info += f" (저자: {metadata['author']})"
            if metadata.get('page'):
                source_info += f" p.{metadata['page']+1}"
        
        formatted_doc = f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>"""
        
        formatted_docs.append(formatted_doc)
    
    return "\n\n".join(formatted_docs)


def filter_docs_by_response(docs, ai_response):
    """LLM 응답에서 실제로 사용된 문서만 필터링"""
    if not docs:
        return []
    
    used_docs = []
    
    for doc in docs:
        metadata = doc.metadata
        
        # 문서 출처 정보 생성
        if metadata.get("source_type") == "qa_data":
            # 상담기록 정보
            lifecycle = metadata.get('lifeCycle', '').strip()
            department = metadata.get('department', '').strip()
            disease = metadata.get('disease', '').strip()
            
            # 응답에 해당 정보가 포함되어 있는지 확인
            if lifecycle and lifecycle in ai_response:
                used_docs.append(doc)
            elif department and department in ai_response:
                used_docs.append(doc)
            elif disease and disease in ai_response:
                used_docs.append(doc)
        else:
            # 서적 정보
            title = metadata.get('title', '').strip()
            author = metadata.get('author', '').strip()
            
            # 응답에 제목이나 저자가 포함되어 있는지 확인
            if title and title in ai_response:
                used_docs.append(doc)
            elif author and author in ai_response:
                used_docs.append(doc)
        
        # 문서 내용이 응답에 포함되어 있는지 확인
        content = doc.page_content[:100].strip()  # 처음 100자 확인
        if content and content in ai_response:
            if doc not in used_docs:
                used_docs.append(doc)
    
    # 사용된 문서가 없으면 원본 첫 번째 문서 포함
    if not used_docs and docs:
        used_docs.append(docs[0])
    
    return used_docs
    # 수의학 서적의 경우
    source_info = f"서적 - {metadata.get('title', '')}"
    if metadata.get('author'):
        source_info += f" (저자: {metadata['author']})"
    if metadata.get('page'):
        source_info += f" p.{metadata['page']+1}"

    formatted_doc = f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>"""

    formatted_docs.append(formatted_doc)

    return "\n\n".join(formatted_docs)


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
    
    st.markdown("")  # 빈 줄 추가
    
    # 채팅 히스토리 초기화
    if "submit_count" not in st.session_state:
        st.session_state.submit_count = 0

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "message_docs" not in st.session_state:
        st.session_state.message_docs = {}  # 메시지 인덱스별 문서 저장
    
    # 2열 레이아웃: 왼쪽(문서) - 오른쪽(채팅)
    col_docs, col_chat = st.columns([1, 2], gap="large")
    
    with col_chat:
        st.markdown("### 💬 대화")
        
        # 채팅 메시지 표시
        chat_container = st.container()
        
        with chat_container:
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
                        docs_to_save = []  # 빈 리스트
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
