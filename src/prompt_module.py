
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# LangChain 임포트
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma 
import chromadb
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from ensemble import EnsembleRetriever

load_dotenv()
if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('OPENAI_API_KEY 없음. .env 확인하세요')
if not os.environ.get('LANGSMITH_API_KEY'):
    raise ValueError('LANGSMITH_API_KEY 없음. env 확인하세요')

os.environ["LANGSMITH_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_PROJECT"] = "pet_rag"
print("LangSmith 연결 완료")



# ---------------------------
# Retriever 생성
# ---------------------------
def get_retriever(vectorstore, k=5):
    """앙상블 리트리버 생성"""
    
    # 기본 리트리버
    retriever = vectorstore.as_retriever(search_kwargs={"k": k}, search_type="similarity")
    
    # BM25 리트리버 생성

    # BM25 전용 문서 로드 (벡터스토어의 임베딩을 Document로 변환 - BM25는 텍스트 기반이므로)
    collection = vectorstore._collection
    doc_count = collection.count()
    
    if doc_count == 0:
        raise ValueError("벡터스토어가 비어있습니다.")
    
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
    
    
    # 기본 리트리버와 BM25를 합쳐
    # 앙상블 리트리버 생성
    retriever_ensemble = EnsembleRetriever(
        retrievers=[retriever, retriever_bm25],
        weights=[0.5, 0.5] #가중치
    )
    
    return retriever_ensemble


# ---------------------------
# 초기화 함수: 벡터스토어 및 LLM 로드
# ---------------------------
def initialize_rag_system(vectorstore_path=r".\data\ChromaDB_bge_m3", collection_name="pet_health_qa_system_bge_m3"):
    """RAG 시스템 초기화 (벡터스토어, LLM, Retriever)"""
    
    # 임베딩 모델 로드
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 벡터스토어 로드
    vectorstore = Chroma(
        persist_directory=vectorstore_path,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    print("벡터스토어가 성공적으로 로드되었습니다!")
        
    # LLM 초기화
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # 앙상블 Retriever 생성 (앙상블)
    retriever = get_retriever(vectorstore, k=5)
    
    return {
        'vectorstore': vectorstore,
        'llm': llm,
        'retriever': retriever,
        'embeddings': embeddings
    }



# ---------------------------
# 프롬프트 정의
# ---------------------------
def get_rag_prompt():
    """
    RAG 시스템용 프롬프트
    """
    return ChatPromptTemplate.from_messages([
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
- 마지막 줄에 반드시 출처를 명시한다:
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
-출처(참고한 모든 문서):

"""),
        ("human", """
문맥: {context}

사용자 질문: {question}
""")
    ])



def get_rewrite_prompt():
    """
    질문 변환 프롬프트 - 맥락 보존하면서 검색 최적화
    """
    return PromptTemplate.from_template("""
다음 질문을 검색에 최적화된 형태로 변환해주세요.
질문에 포함된 핵심 정보와 맥락은 모두 유지하되, 검색에 중요한 키워드를 중심으로 재구성해주세요.

[변환 규칙]
1. 반려동물 종류, 나이, 크기 등 중요한 정보는 반드시 포함
2. 증상, 상황, 기간 등 구체적인 맥락 정보 유지  
3. 불필요한 접속사, 감탄사, 중복 표현만 제거
4. 의학적 키워드가 있다면 우선적으로 포함

원본 질문: {question}

검색 최적화된 질문:
""")



def self_check_prompt():
    '''
    문서 필터링 프롬프트 
    '''
    return PromptTemplate.from_template("""
당신은 검색된 문서가 사용자 질문과 실제로 관련이 있는지 판단하는 AI 필터입니다.

사용자 질문: {question}

문서 내용: \"\"\"{doc}\"\"\"

[판단 기준]
1. 단순히 키워드만 일치하는 것이 아니라 맥락적으로도 연관성이 있는가?
2. 문서가 질문에 대한 구체적인 답변이나 도움이 되는 정보를 포함하고 있는가?
3. 문서가 질문의 핵심 주제와 관련됐는가?

[Keep 조건]
- 질문에 대한 직접적인 답변을 제공하는 경우
- 질문과 관련된 증상, 원인, 치료법 등이 포함된 경우
- 질문의 주제와 동일한 질병이나 상황을 다루는 경우

[Drop 조건] 
- 질문과 완전히 다른 주제를 다루는 경우
- 키워드만 일치하고 실제 내용은 무관한 경우
- 너무 일반적이거나 모호해서 도움이 되지 않는 경우

위 기준에 따라 판단하여 "Keep" 또는 "Drop"만 출력하세요.

판단:""")



# Self_check_retriver 함수 (LLM이 각 문서를 보고 KEEP/DROP 판단)
def self_check_retriver(question):
    '''
    이 함수는 사용자의 질문을 받아 검색된 문서들을 LLM이 검토하게 합니다. 
    LLM은 각 문서가 질문에 도움이 되는지 판단해 KEEP/DROP을 결정합니다. 
    결과적으로 KEEP인 문서만 반환합니다.
    '''
    #0. mini chain : 문서 keep or drop ?
    mini_chain = self_check_prompt | llm | StrOutputParser()

    # 1. 문서 검색
    found_docs = retriever.invoke(question)
    print(f'검색된 문서 개수: {len(found_docs)}')

    # 2. 문서별로 KEEP/DROP 판단
    kept_docs = []

    for doc in found_docs:
        decision = mini_chain.invoke({'question': question, 'doc': doc.page_content})
        print(f'\n문서 내용: {doc.page_content}\n판단: {decision}')

        if decision.strip().lower() == 'keep':
            kept_docs.append(doc)

    if len(kept_docs) == 0:
        print('모든 문서가 Drop되었습니다. 원래 검색된 문서들을 반환합니다.')
        kept_docs = found_docs  # 모든 문서가 Drop되면 원래 검색된 문서 반환

    print(f'\n최종 선택된 문서 개수: {len(kept_docs)}')

    return kept_docs






# ---------------------------
# 문서 포맷팅 함수
# ---------------------------
def format_docs(kept_docs):
    """kEEP인 문서를 출처 정보와 함께 포맷팅"""
    formatted_docs = []
    for doc in kept_docs:
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
            lifecycle = metadata.get('lifeCycle', '').strip()
            department = metadata.get('department', '').strip()
            disease = metadata.get('disease', '').strip()
            
            if lifecycle and lifecycle in ai_response:
                used_docs.append(doc)
            elif department and department in ai_response:
                used_docs.append(doc)
            elif disease and disease in ai_response:
                used_docs.append(doc)
        else:
            title = metadata.get('title', '').strip()
            author = metadata.get('author', '').strip()
            
            if title and title in ai_response:
                used_docs.append(doc)
            elif author and author in ai_response:
                used_docs.append(doc)
        
        # 문서 내용 확인
        content = doc.page_content[:100].strip()
        if content and content in ai_response:
            if doc not in used_docs:
                used_docs.append(doc)
    
    if not used_docs and docs:
        used_docs.append(docs[0])
    
    return used_docs




# ---------------------------
# 테스트 실행 (직접 실행 시에만)
# ---------------------------




'''
벡터 DB 불러오기
불러올때 생성시 임베딩 모델/컬렉션 이름과 동일해야 합니다!
'''


# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# bge_m3 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},  # GPU 사용시 'cuda'로 변경
    encode_kwargs={'normalize_embeddings': True}  # bge-m3는 정규화 권장
)
#벡터스토어 로드
vectorstore = Chroma(
# persist_directory=r"..\data\ChromaDB_openai", #DB 저장한 경로
# collection_name="pet_health_qa_system",
persist_directory=r"..\data\ChromaDB_bge_m3", #DB 저장한 경로
collection_name="pet_health_qa_system_bge_m3",
embedding_function=embeddings)
print("벡터스토어가 성공적으로 로드되었습니다!")

#컬렉션 확인
client = chromadb.PersistentClient(path=r"..\data\ChromaDB_bge_m3")
collections = client.list_collections()
print("사용 가능한 컬렉션:", [c.name for c in collections])


#프롬포트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
        ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
문맥에 없는 정보는 절대로 추측하거나 생성하지 마세요.

[사용 가능한 정보 유형]
- medical_data: 수의학 서적 또는 논문
- qa_data: 보호자-수의사 상담 기록 (생애주기 / 과 / 질병 태그 포함)

[할루시네이션 방지 규칙]
1. 문맥에 없는 정보는 사용하지 마세요.
2. 관련 정보가 없다면 “해당 질문과 관련된 문서를 찾지 못했습니다. ”라고 답변하세요.
3. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
4. **질문에 합당한 답변만 제공하세요. 거짓 정보나 불필요한 정보는 제외하세요.**

[응답 규칙]
- 보호자가 작성한 반려견 상태를 2~3문장으로 요약한다.
- 문맥에서 확인된 가능한 원인을 구체적으로 설명한다. 
  (문맥에 없다면 “문서에 해당 정보가 없습니다”라고 쓴다)
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
-출처(참고한 모든 문서)

"""),
("human",
"""
문맥: {context}

사용자 질문: {question}
""")
    ])


# rewrite 프롬프트 
# 사용자의 질문을 키워드 중심으로 정리해 llm 전달 (검색 최적화된 형태로 질문 바꿔줌) 
rewrite_prompt= PromptTemplate.from_template(
    '''
    다음 질문을 검색에 더 적합한 형태로 변환해 주세요.
    키워드 중심으로 명확하게 바꿔주세요
    변환된 검색어만 출력하세요

    원본 질문: {question}
    변환된 검색어:
    ''')



#문서 포맷팅 함수
def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata
        
        # 데이터 유형에 따라 출처 정보 구성
        if metadata.get("source_type") == "qa_data":
            source_info = f"상담기록 - {metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
        else:
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




# 예시 질문으로 프롬포트 성능 테스트
# 1. 무조건 대답해야만 하는거 , 애매한거, 대답 절대 못해야되는거
query = [
    "강아지 파보바이러스 증상은 무엇인가요?",
    "자견 시기 예방접종 스케줄을 알려주세요",
    # "강아지 슬개골 탈구 치료 방법은 무엇인가요?",
    "노령견이 신부전 진단을 받았는데, 식이관리와 약물치료를 병행해야 하나요?",
    "성견의 피부 알레르기와 외이염이 동시에 있을 때 치료 순서는 어떻게 되나요?",
    # "자견이 설사와 구토를 동시에 하는데 응급상황인지 알려주세요",
    # "10살 된 노령견이 갑자기 밥을 안 먹고 기력이 없는데, 어떤 질환을 의심해야 하나요?",
    "중성화 수술 후 체중이 늘어난 성견의 적절한 운동량과 식이량은 어떻게 조절해야 하나요?",
    "강아지 암 예방을 위한 백신이 있나요?",
    "강아지가 초콜릿을 먹었을 때 어떤 약을 먹이면 되나요?"
]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#기본 리트리버 
# retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="similarity") #리트리버 변경 가능

#리트리버 성능 test
retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="similarity") #리트리버 변경 가능
# retriever_mmr = vectorstore.as_retriever(
#     search_type="mmr",
#     search_kwargs={
#         "k": 5,              # 최종 반환 문서 수
#         "fetch_k": 20,       # 초기 검색 문서 수 (많을수록 다양한 후보 확보)
#         "lambda_mult": 0.7   # 0~1 사이 값 (1에 가까울수록 유사도 우선, 0에 가까울수록 다양성 우선)
#     }
# )
# BM25 리트리버 생성 (벡터스토어에서 문서 추출 필요)
# ChromaDB에서 모든 문서를 직접 가져오기
collection = vectorstore._collection
doc_count = collection.count()
print(f"벡터스토어 총 문서 수: {doc_count}개")

if doc_count == 0:
    raise ValueError("벡터스토어가 비어있습니다. 먼저 문서를 추가해주세요.")

# ChromaDB의 get() 메서드를 사용하여 모든 문서 가져오기
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
retriever_dict = {
    # "유사도 검색(Similarity Search)": retriever,
    # "MMR 검색(MMR Search)": retriever_mmr,
    # "BM25 검색(BM25 Search)": retriever_bm25,
    "앙상블 검색(Ensemble Search)": retriever_ensemble
}


rewrite_chain =  rewrite_prompt | llm | StrOutputParser()
rag_chain = prompt | llm | StrOutputParser()

for name, retriever in retriever_dict.items():
    print(f"=== {name} 결과 ===")

    for q in query:
        docs = retriever.invoke(q)
        context = format_docs(docs)
        transformed = rewrite_chain.invoke({'question' : q}) #rewrite_chain의 출력(question 키워드)을 transformed에 저장
        generation = rag_chain.invoke({"context": context, "question": transformed})
        print("-"*30)
        print(f'원본 query : {q}\n')
        print(f'transformed query (핵심 키워드 추출) : {transformed}\n')
        print(f"답변: {generation}\n")

# 