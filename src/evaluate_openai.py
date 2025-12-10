
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# RAGAS 평가 및 CSV 저장을 위한 임포트
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from ragas.embeddings import LangchainEmbeddingsWrapper
from datasets import Dataset
import pandas as pd
import csv

# LangChain 최신 버전 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma 
import chromadb
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

# LangGraph 관련 임포트
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from typing import List
from ensemble import EnsembleRetriever

# base_dir 정의 (파일 경로 설정)
base_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv()
if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('.env 확인하세요. key가 없습니다')
# if not os.environ.get('LANGSMITH_API_KEY'):
#     raise ValueError('LANGSMITH_API_KEY 없음. env 확인해주세요')


'''
LangSmith 연결(env 셋팅 돼있어야 합니다!)
# pip install -U langchain langsmith (한번만 실행)
'''


# os.environ["LANGSMITH_TRACING_V2"] = "true" #기본값 false
# os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGSMITH_PROJECT"]="pet_rag" #프로젝트 이름
# print("LangSmith 연결 완료")




'''
벡터 DB 불러오기
불러올때 생성시 임베딩 모델/컬렉션 이름과 동일해야 합니다!
'''


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
# RAGAS용 embeddings wrapper 생성
ragas_embeddings = LangchainEmbeddingsWrapper(embeddings=embeddings)

#벡터스토어 로드 (절대 경로 사용)
chroma_path = os.path.join(base_dir, '..', 'data', 'ChromaDB_openai')
vectorstore = Chroma(
persist_directory=chroma_path,
collection_name="pet_health_qa_system",
embedding_function=embeddings)
print("벡터스토어가 성공적으로 로드되었습니다!")

#컬렉션 확인
client = chromadb.PersistentClient(path=chroma_path)
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




# RAGAS 평가용 테스트 데이터셋 로드 (CSV 파일)
import json

# CSV 파일에서 데이터셋 로드 (절대 경로 사용)
csv_path = os.path.join(base_dir, '..', 'output', 'pet_test_dataset_openai.csv')
dataset_df = pd.read_csv(csv_path)

# 질문과 답변(reference) 추출
query = dataset_df['user_input'].tolist()
ground_truths = dataset_df['reference'].tolist()

print(f"✓ 테스트 데이터셋 로드 완료: {len(query)}개 Q&A 쌍 로드됨")
print(f"  - 사용 데이터: pet_test_dataset_openai.csv")

# 디버깅: ground_truths 확인
print(f"\n[디버깅 정보]")
print(f"  - 질문 수: {len(query)}")
print(f"  - Ground Truth 수: {len(ground_truths)}")
print(f"  - 첫 번째 질문: {query[0][:50]}...")
print(f"  - 첫 번째 Ground Truth: {ground_truths[0][:50] if ground_truths[0] else 'None'}...")


llm = ChatOpenAI(model="gpt-4.1", temperature=0)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="similarity") #리트리버 변경 가능
retriever_mmr = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,              # 최종 반환 문서 수
        "fetch_k": 20,       # 초기 검색 문서 수 (많을수록 다양한 후보 확보)
        "lambda_mult": 0.7   # 0~1 사이 값 (1에 가까울수록 유사도 우선, 0에 가까울수록 다양성 우선)
    }
)
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
    "유사도 검색(Similarity Search)": retriever,
    "MMR 검색(MMR Search)": retriever_mmr,
    "BM25 검색(BM25 Search)": retriever_bm25,
    "앙상블 검색(Ensemble Search)": retriever_ensemble
}
rewrite_chain =  rewrite_prompt | llm | StrOutputParser()
rag_chain = prompt | llm | StrOutputParser()



# RAGAS 평가를 위한 데이터 수집 (배치 처리 방식)
evaluation_results = []

# 배치 크기 설정 (타임아웃 방지)
BATCH_SIZE = 5  # 한 번에 5개씩 평가 (필요시 조정: 2-10 범위 권장)

for name, temp_retriever in retriever_dict.items():
    print(f"\n=== {name} RAGAS 평가 시작 ===\n")
    
    # 평가를 위한 데이터 준비
    questions = []
    answers = []
    contexts_list = []
    transformed_queries = []
    
    for i, q in enumerate(query):
        docs = temp_retriever.invoke(q)
        context = format_docs(docs)
        
        transformed = rewrite_chain.invoke({'question': q})
        generation = rag_chain.invoke({"context": context, "question": transformed})
        
        # 평가 데이터 수집
        questions.append(q)
        answers.append(generation)
        # RAGAS는 contexts를 리스트 형태로 요구 (각 문서를 개별 요소로)
        contexts_list.append([doc.page_content for doc in docs])
        transformed_queries.append(transformed)
    
    # 배치 단위로 평가 수행
    batch_results = []
    total_batches = (len(questions) - 1) // BATCH_SIZE + 1
    
    for batch_idx in range(0, len(questions), BATCH_SIZE):
        batch_end = min(batch_idx + BATCH_SIZE, len(questions))
        batch_num = batch_idx // BATCH_SIZE + 1
        
        print(f"  [{batch_num}/{total_batches}] 배치 평가 중... (질문 {batch_idx+1}-{batch_end})")
        
        # 배치 데이터 준비
        batch_dataset_dict = {
            "user_input": questions[batch_idx:batch_end],
            "response": answers[batch_idx:batch_end],
            "retrieved_contexts": contexts_list[batch_idx:batch_end],
            "reference": ground_truths[batch_idx:batch_end],
        }
        
        batch_dataset = Dataset.from_dict(batch_dataset_dict)
        
        try:
            # RAGAS 평가 실행 - 4대 지표 모두 포함
            # context_recall: 검색된 컨텍스트가 ground truth를 얼마나 포함하는지
            # context_precision: 검색된 컨텍스트가 얼마나 관련성이 있는지
            # answer_relevancy: 답변이 질문과 관련이 있는지
            # faithfulness: 답변이 컨텍스트에 기반하는지 (할루시네이션 방지)
            result = evaluate(
                dataset=batch_dataset,
                metrics=[
                    context_recall,      # 검색된 문서의 recall
                    context_precision,   # 검색된 문서의 precision
                    faithfulness,        # 답변이 컨텍스트에 기반하는지
                    answer_relevancy,    # 답변이 질문과 관련이 있는지
                ],
                llm=llm,                # LLM을 evaluate 함수에 전달
                embeddings=ragas_embeddings,  # Embeddings를 evaluate 함수에 전달
            )
            
            # 결과를 DataFrame으로 변환
            batch_results_df = result.to_pandas()
            batch_results.append(batch_results_df)
            print(f"  ✓ 배치 {batch_num} 완료")
            
        except Exception as e:
            print(f"  ⚠️  배치 {batch_num} 평가 중 오류 발생: {str(e)}")
            continue
    
    # 모든 배치 결과 합치기
    if batch_results:
        results_df = pd.concat(batch_results, ignore_index=True)
        
        # 추가 정보 추가
        results_df['retriever_name'] = name
        results_df['original_question'] = questions
        results_df['transformed_query'] = transformed_queries
        results_df['answer'] = answers
        
        # 컬럼 순서 재정렬 - RAGAS 4대 지표 포함
        column_order = [
            'retriever_name',
            'original_question',
            'transformed_query',
            'answer',
            'context_recall',      # RAGAS 4대 지표 1
            'context_precision',   # RAGAS 4대 지표 2
            'faithfulness',        # RAGAS 4대 지표 3
            'answer_relevancy',    # RAGAS 4대 지표 4
        ]
        
        # 존재하는 컬럼만 선택
        available_columns = [col for col in column_order if col in results_df.columns]
        results_df = results_df[available_columns]
        
        evaluation_results.append(results_df)
        print(f"✓ {name} 평가 완료")

# 모든 결과를 하나의 DataFrame으로 합치기
if evaluation_results:
    final_results = pd.concat(evaluation_results, ignore_index=True)
    
    # CSV 파일로 저장 (절대 경로 사용)
    # Excel 호환성을 위해 quoting과 escapechar 설정
    csv_filename = os.path.join(base_dir, '..', 'output', 'ragas_evaluation_results_openai.csv')
    final_results.to_csv(
        csv_filename, 
        index=False, 
        encoding='utf-8-sig',
        quoting=csv.QUOTE_ALL,  # 모든 필드를 따옴표로 감싸서 Excel 호환성 향상
        escapechar='\\',  # 이스케이프 문자 설정
        lineterminator='\n'  # 줄바꿈 문자 명시
    )
    print(f"\n평가 결과가 '{csv_filename}' 파일에 저장되었습니다!")
    print(f"총 {len(final_results)}개의 질문이 평가되었습니다.")
    print("\n=== RAGAS 4대 지표 평균 점수 ===")
    # RAGAS 4대 지표
    metric_columns = [
        'context_recall',
        'context_precision', 
        'faithfulness',
        'answer_relevancy'
    ]
    
    metric_descriptions = {
        'context_recall': 'Context Recall (검색 재현율)',
        'context_precision': 'Context Precision (검색 정확도)',
        'faithfulness': 'Faithfulness (충실성)',
        'answer_relevancy': 'Answer Relevancy (답변 관련성)'
    }
    
    for metric in metric_columns:
        if metric in final_results.columns:
            avg_score = final_results[metric].mean()
            print(f"  {metric_descriptions[metric]}: {avg_score:.4f}")
else:
    print("평가할 데이터가 없습니다.")