
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
from prompt import get_rewrite_prompt, get_rag_prompt, self_check_prompt # 프롬포트 불러오기
from utils import format_docs, get_retriever, self_check_retriver, initialize_rag_system, filter_docs_by_response #유틸리티 함수 불러오기
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
# 테스트 실행 (직접 실행 시에만)
# ---------------------------
'''
벡터 DB 불러오기
불러올때 생성시 임베딩 모델/컬렉션 이름과 동일해야 합니다!
'''



# bge_m3 임베딩 모델 로드
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={'device': 'cpu'},  # GPU 사용시 'cuda'로 변경
    encode_kwargs={'normalize_embeddings': True}  # bge-m3는 정규화 권장
)
#벡터스토어 로드
vectorstore = Chroma(
persist_directory=r"..\data\ChromaDB_bge_m3", #DB 저장한 경로
collection_name="pet_health_qa_system_bge_m3",
embedding_function=embeddings)
print("벡터스토어가 성공적으로 로드되었습니다!")

#컬렉션 확인
client = chromadb.PersistentClient(path=r"..\data\ChromaDB_bge_m3")
collections = client.list_collections()
print("사용 가능한 컬렉션:", [c.name for c in collections])

