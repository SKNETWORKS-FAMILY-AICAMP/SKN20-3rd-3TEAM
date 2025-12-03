"""
디버깅 로그를 포함한 간단한 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# 환경설정
import os
from dotenv import load_dotenv
load_dotenv()

# 모듈 import
from src.embeddings import get_embedding_model, load_vectorstore
from src.retrieval import create_retriever
from src.pipeline import LangGraphRAGPipeline

print("="*80)
print("LangGraph CRAG 파이프라인 테스트 시작")
print("="*80)

try:
    # 1. 임베딩 모델 로드
    print("\n[1/3] 임베딩 모델 로드 중...")
    embedding_model = get_embedding_model("openai")
    print("✅ 임베딩 모델 로드 완료\n")
    
    # 2. 벡터스토어 로드
    print("[2/3] 벡터스토어 로드 중...")
    vectorstore = load_vectorstore(
        embedding_model,
        persist_directory="./chroma_db",
        collection_name="rag_collection"
    )
    print("✅ 벡터스토어 로드 완료\n")
    
    # 3. Retriever 생성
    print("[3/3] Retriever 생성 중...")
    retriever = create_retriever(
        vectorstore,
        k=10,
        rerank_k=5,
        use_reranking=True,
        embedding_model=embedding_model
    )
    print("✅ Retriever 생성 완료\n")
    
    # LangGraph CRAG 파이프라인 생성
    print("\n" + "="*80)
    print("LangGraph CRAG 파이프라인 초기화")
    print("="*80)
    pipeline = LangGraphRAGPipeline(retriever, debug=True)
    
    # 테스트 쿼리
    print("\n\n" + "#"*80)
    print("# 테스트 쿼리: 강아지 두드러기 증상")
    print("#"*80)
    
    result = pipeline.rag_pipeline_with_sources("강아지 몸에 두드러기가 났어요. 어떻게 하면 좋을까요?")
    
    print("\n\n" + "="*80)
    print("📋 최종 답변")
    print("="*80)
    print(result['answer'])
    print("\n")

except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()

