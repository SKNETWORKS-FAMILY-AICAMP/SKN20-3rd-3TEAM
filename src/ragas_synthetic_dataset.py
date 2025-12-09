# ragas_testset_generator.py (새 파일 생성)

import os
from dotenv import load_dotenv
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context, conditional
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset.extractor import KeyphraseExtractor
from ragas.testset.docstore import InMemoryDocumentStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import pandas as pd

load_dotenv()

# 기존 벡터스토어에서 문서 로드
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},  # GPU 사용시 'cuda'로 변경
    encode_kwargs={'normalize_embeddings': True}  # bge-m3는 정규화 권장
)
vectorstore = Chroma(
    persist_directory=r"..\data\ChromaDB_bge_m3",
    collection_name="pet_health_qa_system_bge_m3",
    embedding_function=embeddings
)

# 벡터스토어에서 모든 문서 가져오기
# 주의: 메모리 사용량 고려하여 필요시 배치 처리
all_docs = vectorstore.similarity_search("", k=1000)  # 또는 필요한 만큼

# LangChain Document 형식으로 변환 (metadata에 filename 필수)
from langchain_core.documents import Document
langchain_docs = []
for doc in all_docs:
    langchain_doc = Document(
        page_content=doc.page_content,
        metadata=doc.metadata
    )
    # filename이 없으면 추가
    if "filename" not in langchain_doc.metadata:
        langchain_doc.metadata["filename"] = langchain_doc.metadata.get("source", "unknown")
    langchain_docs.append(langchain_doc)

# LLM 및 Embeddings 설정
generator_llm = ChatOpenAI(model="gpt-4.1")
critic_llm = ChatOpenAI(model="gpt-4.1")
ragas_embeddings = LangchainEmbeddingsWrapper(embeddings=embeddings)

# DocumentStore 설정
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
langchain_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
keyphrase_extractor = KeyphraseExtractor(llm=langchain_llm)

docstore = InMemoryDocumentStore(
    splitter=splitter,
    embeddings=ragas_embeddings,
    extractor=keyphrase_extractor,
)

# TestSetGenerator 생성
generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    ragas_embeddings,
    docstore=docstore,
)

# 질문 유형별 분포 설정
# 반려견 질병 도메인에 맞게 조정 가능
distributions = {
    simple: 0.4,           # 간단한 질문 (예: "파보바이러스 증상은?")
    reasoning: 0.2,        # 추론 필요 (예: "신부전과 식이관리 병행?")
    multi_context: 0.2,    # 여러 맥락 (예: "알레르기와 외이염 동시 치료")
    conditional: 0.2       # 조건부 (예: "중성화 후 체중 증가 시 운동량?")
}

# 테스트셋 생성
print("테스트셋 생성 시작...")
testset = generator.generate_with_langchain_docs(
    documents=langchain_docs,
    test_size=50,  # 생성할 질문 수 (필요에 따라 조정)
    distributions=distributions,
    with_debugging_logs=True
)

# DataFrame으로 변환 및 저장
test_df = testset.to_pandas()
test_df.to_csv("../output/ragas_synthetic_dataset.csv", index=False, encoding='utf-8-sig')
print(f"생성 완료! {len(test_df)}개의 질문이 '../output/ragas_synthetic_dataset.csv'에 저장되었습니다.")
print("\n생성된 질문 샘플:")
print(test_df[['question', 'evolution_type']].head(10))