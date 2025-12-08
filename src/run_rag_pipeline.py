"""
RAG Pipeline 실행 스크립트
전체 RAG 파이프라인을 실행하는 메인 스크립트
"""

import os
import sys

# 현재 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processing.data_processor import batch_preprocess_documents
from data_processing.vector_store_manager import VectorStoreManager
from retrieval.rag_handler import perform_rag_search, get_retriever
from generation.llm_generator import generate_response, rewrite_query


def create_vectorstore():
    """
    벡터스토어 생성 워크플로우
    """
    print("\n" + "=" * 60)
    print("🚀 벡터스토어 생성 시작")
    print("=" * 60)
    
    # 1. 데이터 경로 설정 (Training 데이터 사용)
    # src 폴더 기준 상대 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    base_path = os.path.join(project_root, "1.데이터", "Training", "02.라벨링데이터")
    
    data_paths = [
        os.path.join(base_path, "TL_질의응답데이터_내과"),
        os.path.join(base_path, "TL_질의응답데이터_안과"),
        os.path.join(base_path, "TL_질의응답데이터_외과"),
        os.path.join(base_path, "TL_질의응답데이터_치과"),
        os.path.join(base_path, "TL_질의응답데이터_피부과"),
    ]
    
    # 2. 데이터 전처리 및 청킹
    print("\n📄 데이터 전처리 및 청킹...")
    chunked_docs = batch_preprocess_documents(data_paths)
    
    if not chunked_docs:
        print("❌ 문서 처리 실패")
        return False
    
    # 3. 벡터스토어 생성
    print("\n💾 벡터스토어 생성...")
    vector_manager = VectorStoreManager()
    success = vector_manager.create_vectorstore(chunked_docs)
    
    if success:
        print("\n✅ 벡터스토어 생성 완료!")
        print("=" * 60)
        return True
    else:
        print("\n❌ 벡터스토어 생성 실패")
        return False


def run_rag_query(query: str, use_rewrite: bool = True):
    """
    RAG 쿼리 실행
    
    Args:
        query: 사용자 쿼리
        use_rewrite: 쿼리 재작성 사용 여부
    """
    print("\n" + "=" * 60)
    print(f"🔍 RAG 쿼리 실행: {query}")
    print("=" * 60)
    
    # 1. 쿼리 재작성 (선택적)
    transformed_query = query
    if use_rewrite:
        print("\n📝 쿼리 재작성...")
        transformed_query = rewrite_query(query)
    
    # 2. 문서 검색
    print("\n🔎 문서 검색...")
    context = perform_rag_search(transformed_query, k=5)
    
    if not context:
        print("❌ 관련 문서를 찾을 수 없습니다.")
        return None
    
    # 3. 응답 생성
    print("\n🤖 응답 생성...")
    response = generate_response(transformed_query, context)
    
    print("\n" + "=" * 60)
    print("📄 최종 응답:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
    return response


def test_rag_pipeline():
    """
    RAG 파이프라인 테스트
    """
    print("\n" + "=" * 60)
    print("🧪 RAG 파이프라인 테스트")
    print("=" * 60)
    
    # 테스트 쿼리들
    test_queries = [
        "우리 강아지가 갑자기 구토를 시작했어요. 며칠 전부터 식욕도 없고 기운이 없어 보여서 걱정입니다. 어떤 원인일 수 있을까요? 집에서 어떻게 돌봐줘야 하나요?",
        "우리 강아지가 노견인데 기침을 하다가 오늘 기절했어요. 의심되는 질환이 뭔지 알려주고, 위험도가 어느정도인가요?",
        "강아지 피부염 증상과 치료 방법을 알려주세요."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*60}")
        print(f"테스트 {i}/{len(test_queries)}")
        print(f"{'='*60}")
        run_rag_query(query, use_rewrite=True)
        input("\n다음 테스트를 진행하려면 Enter를 누르세요...")


def main():
    """
    메인 함수
    """
    print("\n" + "=" * 60)
    print("🎯 RAG Pipeline - 메인 메뉴")
    print("=" * 60)
    print("1. 벡터스토어 생성")
    print("2. RAG 쿼리 실행")
    print("3. 테스트 실행")
    print("4. 종료")
    print("=" * 60)
    
    while True:
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == "1":
            create_vectorstore()
        
        elif choice == "2":
            query = input("\n질문을 입력하세요: ").strip()
            if query:
                run_rag_query(query, use_rewrite=True)
            else:
                print("질문을 입력해주세요.")
        
        elif choice == "3":
            test_rag_pipeline()
        
        elif choice == "4":
            print("\n👋 프로그램을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-4 중에서 선택하세요.")


if __name__ == "__main__":
    main()
