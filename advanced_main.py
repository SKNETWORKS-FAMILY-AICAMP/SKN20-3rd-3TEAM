"""
고급 RAG 시스템 메인 실행 파일
반려동물 전문 QA 및 병원 안내 어시스턴트
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# src 모듈 import
sys.path.append(str(Path(__file__).parent))
from src.ingestion import ingest_data
from src.chunking import chunk_documents_with_token_range
from src.embeddings import get_embedding_model, create_vectorstore, load_vectorstore
from src.advanced_rag_pipeline import AdvancedRAGPipeline


def setup_advanced_rag_system(
    data_dir: str = "data/raw/disease",
    persist_directory: str = "./chroma_db",
    collection_name: str = "rag_collection",
    embedding_model_type: str = "openai",
    rebuild_vectorstore: bool = False
):
    """
    고급 RAG 시스템 설정
    
    Args:
        data_dir: 데이터 디렉토리 경로
        persist_directory: 벡터 DB 저장 디렉토리
        collection_name: 컬렉션 이름
        embedding_model_type: 임베딩 모델 타입 ("openai" 또는 "huggingface")
        rebuild_vectorstore: 벡터스토어 재구축 여부
        
    Returns:
        AdvancedRAGPipeline 객체
    """
    print("=" * 80)
    print("🚀 고급 RAG 시스템 설정 중...")
    print("=" * 80)
    
    # 1. 임베딩 모델 생성
    print("\n[1/4] 임베딩 모델 로드 중...")
    embedding_model = get_embedding_model(embedding_model_type)
    print(f"✓ 임베딩 모델 로드 완료: {embedding_model_type}")
    
    # 2. 벡터스토어 로드 또는 생성
    print("\n[2/4] 벡터스토어 처리 중...")
    if rebuild_vectorstore or not os.path.exists(persist_directory):
        # 데이터 ingestion
        print("\n[2-1] 데이터 ingestion 중...")
        documents = ingest_data(data_dir)
        
        # Chunking
        print("\n[2-2] 문서 chunking 중...")
        chunked_docs = chunk_documents_with_token_range(
            documents,
            min_tokens=300,
            max_tokens=500,
            overlap_ratio=0.25
        )
        print(f"✓ {len(chunked_docs)}개의 청크 생성 완료")
        
        # 벡터스토어 생성
        print("\n[2-3] 벡터스토어 생성 중...")
        vectorstore = create_vectorstore(
            chunked_docs,
            embedding_model,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        print("✓ 벡터스토어 생성 완료")
    else:
        # 기존 벡터스토어 로드
        vectorstore = load_vectorstore(
            embedding_model,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        print("✓ 기존 벡터스토어 로드 완료")
    
    # 3. 고급 RAG 파이프라인 생성
    print("\n[3/4] 고급 RAG 파이프라인 생성 중...")
    pipeline = AdvancedRAGPipeline(
        vectorstore=vectorstore,
        hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json",
        llm_model="gpt-4o-mini",
        score_threshold=0.6
    )
    print("✓ 파이프라인 생성 완료 (분류 + 의료 + 병원 + 일반 처리)")
    
    print("\n[4/4] 시스템 준비 완료!")
    print("=" * 80)
    
    return pipeline


def run_example_queries():
    """
    예시 질문 실행
    """
    example_queries = [
        # 의료 질문 (Type A)
        "개의 피부염 증상은 무엇인가요?",
        "강아지가 구토를 하면 어떻게 해야 하나요?",
        "고양이의 신부전 치료법을 알려주세요.",
        
        # 병원 질문 (Type B)
        "강남구의 동물병원을 찾아주세요.",
        "서울에서 24시간 응급진료를 하는 병원이 있나요?",
        
        # 일반 질문 (Type C)
        "반려동물을 처음 키우는데 어떤 준비가 필요한가요?",
    ]
    
    print("\n" + "=" * 80)
    print("📋 예시 질문 실행")
    print("=" * 80)
    
    pipeline = setup_advanced_rag_system()
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"[예시 {i}] {query}")
        print("=" * 80)
        
        result = pipeline.process_question(query)
        
        # 결과 출력
        print("\n📝 답변:")
        print(result['formatted_answer'])
        
        # 분류 정보 출력
        print(f"\n📊 분류 정보:")
        print(f"  유형: {result['classification_type']}")
        print(f"  신뢰도: {result['classification_confidence']:.2%}")
        print(f"  사유: {result['classification_reason']}")
        
        print("\n" + "-" * 80)
        input("다음 질문으로 진행하려면 Enter를 누르세요...")


def run_batch_queries_from_file():
    """
    파일에서 질문을 읽어 배치 처리
    """
    query_file = "queries.txt"
    
    if not os.path.exists(query_file):
        print(f"쿼리 파일 '{query_file}'을(를) 찾을 수 없습니다.")
        return
    
    with open(query_file, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f if line.strip()]
    
    print(f"\n{len(queries)}개의 질문을 로드했습니다.")
    
    pipeline = setup_advanced_rag_system()
    results = pipeline.batch_process_questions(queries)
    
    # 결과 저장
    pipeline.save_results(results, "batch_results.json")


def main():
    """
    메인 실행 함수
    """
    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 경고: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("환경변수를 설정하거나 .env 파일을 생성하세요.")
        input("\n계속 진행하려면 Enter를 누르세요...")
    
    # RAG 시스템 설정
    pipeline = setup_advanced_rag_system(
        data_dir="data/Validation/01.원천데이터",
        persist_directory="./chroma_db",
        collection_name="rag_collection",
        embedding_model_type="openai",
        rebuild_vectorstore=False
    )
    
    # 메뉴 표시
    print("\n" + "=" * 80)
    print("🐾 반려동물 전문 QA 및 병원 안내 어시스턴트")
    print("=" * 80)
    print("\n메뉴:")
    print("  1. 예시 질문 실행")
    print("  2. 대화형 모드")
    print("  3. 배치 처리 (queries.txt에서 읽기)")
    print("  4. 종료")
    print("=" * 80)
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        run_example_queries()
    elif choice == "2":
        pipeline.interactive_mode()
    elif choice == "3":
        run_batch_queries_from_file()
    elif choice == "4":
        print("프로그램을 종료합니다.")
    else:
        print("유효한 선택이 아닙니다.")


if __name__ == "__main__":
    main()

