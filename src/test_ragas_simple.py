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

# LangChain 최신 버전 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma 
import chromadb
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from ensemble import EnsembleRetriever

# base_dir 정의 (파일 경로 설정)
base_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv()
if not os.environ.get('OPENAI_API_KEY'):
    raise ValueError('.env 확인하세요. key가 없습니다')

print("=" * 60)
print("RAGAS 간단 테스트 (2개 샘플로 빠른 테스트)")
print("=" * 60)

# 벡터스토어 로드
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
ragas_embeddings = LangchainEmbeddingsWrapper(embeddings=embeddings)

chroma_path = os.path.join(base_dir, '..', 'data', 'ChromaDB_openai')
vectorstore = Chroma(
    persist_directory=chroma_path,
    collection_name="pet_health_qa_system",
    embedding_function=embeddings)
print("✓ 벡터스토어 로드 완료")

# 테스트 데이터셋 로드
csv_path = os.path.join(base_dir, '..', 'output', 'pet_test_dataset_openai.csv')
dataset_df = pd.read_csv(csv_path)

# 처음 2개만 사용
query = dataset_df['user_input'].tolist()[:2]
ground_truths = dataset_df['reference'].tolist()[:2]

print(f"\n[테스트 데이터]")
print(f"  - 질문 수: {len(query)}")
print(f"  - Ground Truth 수: {len(ground_truths)}")
print(f"  - 첫 번째 질문: {query[0][:50]}...")
print(f"  - 첫 번째 Ground Truth: {ground_truths[0][:50]}...")

# 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다."""),
    ("human", "문맥: {context}\n\n사용자 질문: {question}")
])

rewrite_prompt = PromptTemplate.from_template(
    '''다음 질문을 검색에 더 적합한 형태로 변환해 주세요.
    원본 질문: {question}
    변환된 검색어:''')

# 문서 포맷팅 함수
def format_docs(docs):
    return "\n\n".join([f"문서: {doc.page_content[:200]}" for doc in docs])

# LLM 및 리트리버
llm = ChatOpenAI(model="gpt-4.1", temperature=0)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="similarity")
rewrite_chain = rewrite_prompt | llm | StrOutputParser()
rag_chain = prompt | llm | StrOutputParser()

# 평가 데이터 수집
print(f"\n[평가 데이터 수집 중...]")
questions = []
answers = []
contexts_list = []

for i, q in enumerate(query):
    print(f"  {i+1}/{len(query)} 처리 중...", end=" ")
    docs = retriever.invoke(q)
    context = format_docs(docs)
    
    transformed = rewrite_chain.invoke({'question': q})
    generation = rag_chain.invoke({"context": context, "question": transformed})
    
    questions.append(q)
    answers.append(generation)
    contexts_list.append([doc.page_content for doc in docs])
    print("완료")

# RAGAS 평가
print(f"\n[RAGAS 평가 실행 중...]")
dataset_dict = {
    "question": questions,
    "answer": answers,
    "contexts": contexts_list,
    "ground_truth": ground_truths,
}

dataset = Dataset.from_dict(dataset_dict)

result = evaluate(
    dataset=dataset,
    metrics=[
        context_recall,
        context_precision,
        faithfulness,
        answer_relevancy,
    ],
    llm=llm,
    embeddings=ragas_embeddings,
)

# 결과 확인
results_df = result.to_pandas()
print(f"\n[평가 결과]")
print(f"컬럼 목록: {list(results_df.columns)}")
print(f"\n점수:")
for col in ['context_recall', 'context_precision', 'faithfulness', 'answer_relevancy']:
    if col in results_df.columns:
        print(f"  {col}: {results_df[col].values}")
    else:
        print(f"  {col}: ❌ 없음")

print("\n" + "=" * 60)

