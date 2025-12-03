"""
고급 RAG 시스템 테스트 스크립트
질문 분류, 의료 QA, 병원 검색 기능 테스트
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
sys.path.append(str(Path(__file__).parent))

from src.ingestion import ingest_data
from src.chunking import chunk_documents_with_token_range
from src.embeddings import get_embedding_model, create_vectorstore, load_vectorstore
from src.question_classifier import QuestionClassifier
from src.medical_qa_handler import MedicalQAHandler
from src.hospital_handler import HospitalHandler
from src.advanced_rag_pipeline import AdvancedRAGPipeline


def test_question_classifier():
    """
    질문 분류 테스트
    """
    print("\n" + "=" * 80)
    print("TEST 1: 질문 분류 테스트")
    print("=" * 80)
    
    classifier = QuestionClassifier()
    
    test_questions = [
        # 의료 질문
        "개의 귀염증 증상과 치료법을 알려주세요.",
        "고양이가 자꾸 구토해요. 뭐가 문제인가요?",
        "벼룩 예방 방법은 무엇인가요?",
        
        # 병원 질문
        "서울 강남구의 동물병원을 찾아주세요.",
        "24시간 응급진료 병원이 있을까요?",
        
        # 일반 질문
        "반려동물 교실을 어디서 찾을 수 있나요?",
        "개와 고양이는 왜 사이가 안 좋나요?",
    ]
    
    for question in test_questions:
        question_type, confidence, reason = classifier.classify(question)
        print(f"\n질문: {question}")
        print(f"  분류: {question_type.name} ({question_type.value})")
        print(f"  신뢰도: {confidence:.2%}")
        print(f"  사유: {reason}")


def test_hospital_handler():
    """
    병원 정보 처리 테스트
    """
    print("\n" + "=" * 80)
    print("TEST 2: 병원 정보 처리 테스트")
    print("=" * 80)
    
    handler = HospitalHandler()
    
    # 통계 출력
    print("\n📊 병원 통계:")
    stats = handler.get_statistics()
    print(f"  총 병원 수: {stats.get('total_hospitals', 0)}")
    print(f"\n  구별 병원 수 (상위 10개):")
    for district, count in stats.get('top_districts', [])[:10]:
        print(f"    • {district}: {count}개")
    
    # 지역별 검색
    print("\n🔍 지역별 검색 테스트:")
    hospitals = handler.get_nearby_hospitals("강남구", limit=5)
    print(f"  강남구의 병원 ({len(hospitals)}개):")
    for i, hospital in enumerate(hospitals[:3], 1):
        print(f"    {i}. {hospital['name']}")
        print(f"       주소: {hospital['address']}")
        print(f"       전화: {hospital['phone']}")


def test_advanced_pipeline():
    """
    고급 RAG 파이프라인 테스트
    """
    print("\n" + "=" * 80)
    print("TEST 3: 고급 RAG 파이프라인 테스트")
    print("=" * 80)
    
    # 벡터스토어 로드
    print("\n벡터스토어 로드 중...")
    embedding_model = get_embedding_model("openai")
    
    if not os.path.exists("./chroma_db"):
        print("벡터스토어가 없습니다. 생성 중...")
        documents = ingest_data("data/Validation/01.원천데이터")
        chunked_docs = chunk_documents_with_token_range(
            documents,
            min_tokens=300,
            max_tokens=500,
            overlap_ratio=0.25
        )
        vectorstore = create_vectorstore(
            chunked_docs,
            embedding_model,
            persist_directory="./chroma_db",
            collection_name="rag_collection"
        )
    else:
        vectorstore = load_vectorstore(
            embedding_model,
            persist_directory="./chroma_db",
            collection_name="rag_collection"
        )
    
    print("✓ 벡터스토어 로드 완료")
    
    # 파이프라인 초기화
    print("\n파이프라인 초기화 중...")
    pipeline = AdvancedRAGPipeline(
        vectorstore=vectorstore,
        hospital_csv_path="data/raw/hospital/서울시_동물병원_인허가_정보.csv",
        llm_model="gpt-4o-mini",
        score_threshold=0.6
    )
    print("✓ 파이프라인 초기화 완료")
    
    # 테스트 질문
    test_queries = [
        # 의료 질문
        "개의 피부염 증상을 알려주세요.",
        # 병원 질문
        "강남구 동물병원을 찾아주세요.",
        # 일반 질문
        "반려동물을 처음 키우는데 어떤 준비가 필요할까요?",
    ]
    
    results = []
    for query in test_queries:
        print(f"\n{'─' * 80}")
        result = pipeline.process_question(query)
        results.append(result)
        
        print(f"\n📝 간단한 답변:")
        answer_preview = result['formatted_answer'][:200] + "..." if len(result['formatted_answer']) > 200 else result['formatted_answer']
        print(answer_preview)
    
    # 결과 저장
    pipeline.save_results(results, "test_results.json")
    print(f"\n✓ 테스트 결과를 test_results.json에 저장했습니다.")


def test_medical_scoring():
    """
    의료 질문의 점수 평가 테스트
    """
    print("\n" + "=" * 80)
    print("TEST 4: 의료 질문 점수 평가 테스트")
    print("=" * 80)
    
    # 벡터스토어 로드
    print("\n벡터스토어 로드 중...")
    embedding_model = get_embedding_model("openai")
    
    if not os.path.exists("./chroma_db"):
        print("벡터스토어 필요 - TEST 3 실행 후 진행하세요.")
        return
    
    vectorstore = load_vectorstore(
        embedding_model,
        persist_directory="./chroma_db",
        collection_name="rag_collection"
    )
    
    # 의료 핸들러 초기화
    handler = MedicalQAHandler(
        vectorstore=vectorstore,
        score_threshold=0.6,
        top_k=5
    )
    
    # 테스트 질문
    test_queries = [
        "개의 벼룩 알러지성 피부염 증상은?",
        "고양이 신부전 치료법",
        "개의 귀감염 원인과 치료",
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        result = handler.handle_medical_question(query)
        
        print(f"\n결과:")
        print(f"  • 내부 문서: {result['internal_search_results']}개")
        print(f"  • 웹 검색 사용: {result['used_web_search']}")
        print(f"  • 근거 점수: {result['relevance_score']:.2%}")
        print(f"  • 상태: {'충분한 근거' if result['relevance_score'] >= 0.6 else '웹 검색 수행'}")


def main():
    """
    메인 테스트 함수
    """
    print("=" * 80)
    print("🧪 고급 RAG 시스템 테스트")
    print("=" * 80)
    
    test_menu = {
        "1": ("질문 분류 테스트", test_question_classifier),
        "2": ("병원 정보 처리 테스트", test_hospital_handler),
        "3": ("의료 질문 점수 평가 테스트", test_medical_scoring),
        "4": ("전체 파이프라인 테스트", test_advanced_pipeline),
        "5": ("모든 테스트 실행", None),
    }
    
    print("\n테스트 메뉴:")
    for key, (name, _) in test_menu.items():
        print(f"  {key}. {name}")
    print("  6. 종료")
    
    choice = input("\n선택 (1-6): ").strip()
    
    if choice == "1":
        test_question_classifier()
    elif choice == "2":
        test_hospital_handler()
    elif choice == "3":
        test_medical_scoring()
    elif choice == "4":
        test_advanced_pipeline()
    elif choice == "5":
        test_question_classifier()
        test_hospital_handler()
        test_medical_scoring()
        test_advanced_pipeline()
    elif choice == "6":
        print("테스트를 종료합니다.")
    else:
        print("유효한 선택이 아닙니다.")


if __name__ == "__main__":
    main()

