# """
# RAG 시스템 메인 실행 파일
# 데이터 ingestion → embedding → retrieval → LLM RAG pipeline 전체 흐름 실행
# """
# import os
# import sys
# from pathlib import Path
# from dotenv import load_dotenv

# # 환경변수 로드
# load_dotenv()

# # src 모듈 import
# sys.path.append(str(Path(__file__).parent))
# from src.ingestion import ingest_data
# from src.chunking import chunk_documents_with_token_range
# from src.embeddings import get_embedding_model, create_vectorstore, load_vectorstore
# from src.retrieval import create_retriever
# from src.pipeline import create_rag_pipeline


# def setup_rag_system(
#     data_dir: str = "data/Validation/01.원천데이터",
#     persist_directory: str = "./chroma_db",
#     collection_name: str = "rag_collection",
#     embedding_model_type: str = "openai",
#     rebuild_vectorstore: bool = False
# ):
#     """
#     RAG 시스템 설정
    
#     Args:
#         data_dir: 데이터 디렉토리 경로
#         persist_directory: 벡터 DB 저장 디렉토리
#         collection_name: 컬렉션 이름
#         embedding_model_type: 임베딩 모델 타입 ("openai" 또는 "huggingface")
#         rebuild_vectorstore: 벡터스토어 재구축 여부
        
#     Returns:
#         RAGPipeline 객체
#     """
#     print("="*60)
#     print("RAG 시스템 설정 중...")
#     print("="*60)
    
#     # 1. 임베딩 모델 생성
#     print("\n[1/5] 임베딩 모델 로드 중...")
#     embedding_model = get_embedding_model(embedding_model_type)
#     print(f"✓ 임베딩 모델 로드 완료: {embedding_model_type}")
    
#     # 2. 벡터스토어 로드 또는 생성
#     print("\n[2/5] 벡터스토어 처리 중...")
#     if rebuild_vectorstore or not os.path.exists(persist_directory):
#         # 데이터 ingestion
#         print("\n[2-1] 데이터 ingestion 중...")
#         documents = ingest_data(data_dir)
        
#         # Chunking
#         print("\n[2-2] 문서 chunking 중...")
#         chunked_docs = chunk_documents_with_token_range(
#             documents,
#             min_tokens=300,
#             max_tokens=500,
#             overlap_ratio=0.25
#         )
#         print(f"✓ {len(chunked_docs)}개의 청크 생성 완료")
        
#         # 벡터스토어 생성
#         print("\n[2-3] 벡터스토어 생성 중...")
#         vectorstore = create_vectorstore(
#             chunked_docs,
#             embedding_model,
#             persist_directory=persist_directory,
#             collection_name=collection_name
#         )
#         print("✓ 벡터스토어 생성 완료")
#     else:
#         # 기존 벡터스토어 로드
#         vectorstore = load_vectorstore(
#             embedding_model,
#             persist_directory=persist_directory,
#             collection_name=collection_name
#         )
#         print("✓ 기존 벡터스토어 로드 완료")
    
#     # 3. Retriever 생성
#     print("\n[3/5] Retriever 생성 중...")
#     retriever = create_retriever(
#         vectorstore,
#         top_k=5
#     )
#     print("✓ Retriever 생성 완료 (top_k=5)")
    
#     # 4. RAG 파이프라인 생성
#     print("\n[4/5] LangGraph CRAG 파이프라인 생성 중...")
#     print("  - 문서 관련성 평가: LLM 기반 자동 평가")
#     print("  - 웹 검색 폴백: 관련 문서 없을 시 Tavily API 활용")
#     pipeline = create_rag_pipeline(
#         retriever,
#         llm_model="gpt-4o-mini",
#         temperature=0.0,
#         use_langgraph=True
#     )
#     print("✓ LangGraph CRAG 파이프라인 생성 완료")
    
#     print("\n[5/5] RAG 시스템 설정 완료!")
#     print("="*60)
    
#     return pipeline


# def main():
#     """
#     메인 실행 함수
#     """
#     # 설정
#     DATA_DIR = "data/Validation/01.원천데이터"
#     PERSIST_DIR = "./chroma_db"
#     COLLECTION_NAME = "rag_collection"
#     EMBEDDING_MODEL_TYPE = "openai"  # "openai" 또는 "huggingface"
#     REBUILD_VECTORSTORE = False  # True로 설정하면 벡터스토어 재구축
    
#     # RAG 시스템 설정
#     pipeline = setup_rag_system(
#         data_dir=DATA_DIR,
#         persist_directory=PERSIST_DIR,
#         collection_name=COLLECTION_NAME,
#         embedding_model_type=EMBEDDING_MODEL_TYPE,
#         rebuild_vectorstore=REBUILD_VECTORSTORE
#     )
    
#     # 예시 쿼리 실행
#     print("\n" + "="*60)
#     print("예시 쿼리 실행")
#     print("="*60)
    
#     example_queries = [
#         "벼룩 알러지성 피부염의 증상은 무엇인가요?",
#         "개에서의 혈액형과 수혈에 대해 설명해주세요.",
#         "알러지 반응의 단계를 설명해주세요.",
#         "자가면역질환에 대해 알려주세요.",
#         "면역결핍의 원인은 무엇인가요?"
#     ]
    
#     for i, query in enumerate(example_queries, 1):
#         print(f"\n{'='*60}")
#         print(f"질문 {i}: {query}")
#         print(f"{'='*60}")
        
#         result = pipeline.rag_pipeline_with_sources(query)
        
#         print(f"\n답변:\n{result['answer']}")
#         print(f"\n참고 문서 수: {result['num_sources']}개")
        
#         if result['sources']:
#             print("\n주요 출처:")
#             for j, source in enumerate(result['sources'][:3], 1):
#                 print(f"  {j}. {source['file_name']} ({source['department']})")
#                 print(f"     제목: {source['title']}")
    
#     # 대화형 모드 (선택사항)
#     print("\n" + "="*60)
#     print("대화형 모드 (종료하려면 'quit' 또는 'exit' 입력)")
#     print("="*60)
    
#     while True:
#         try:
#             query = input("\n질문을 입력하세요: ").strip()
            
#             if query.lower() in ['quit', 'exit', '종료', 'q']:
#                 print("프로그램을 종료합니다.")
#                 break
            
#             if not query:
#                 continue
            
#             result = pipeline.rag_pipeline_with_sources(query)
            
#             print(f"\n답변:\n{result['answer']}")
#             print(f"\n참고 문서 수: {result['num_sources']}개")
            
#         except KeyboardInterrupt:
#             print("\n\n프로그램을 종료합니다.")
#             break
#         except Exception as e:
#             print(f"오류 발생: {str(e)}")


# if __name__ == "__main__":
#     # OpenAI API 키 확인
#     if not os.getenv("OPENAI_API_KEY"):
#         print("경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
#         print("환경변수를 설정하거나 .env 파일을 생성하세요.")
#         print("\n계속 진행하려면 Enter를 누르세요...")
#         input()
    
#     main()

