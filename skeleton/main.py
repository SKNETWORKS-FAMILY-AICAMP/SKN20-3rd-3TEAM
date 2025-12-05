"""
Main Workflow Module
전체 워크플로우 오케스트레이션 (Orchestration)

역할:
  - 8개 핵심 모듈 통합 조합
  - 엔드-투-엔드 쿼리 처리 파이프라인
  - 색인 구축 워크플로우 (indexing_workflow)
  - 쿼리 처리 워크플로우 (main_workflow)
  - 배치 처리 (batch_workflow)
"""

import time
from typing import Dict, List, Literal

# ==================== 모듈 임포트 ====================
# 문서 처리
from data_processor import preprocess_document, batch_preprocess_documents
from vector_store_manager import embed_and_index_chunks

# 입력 분류
from input_classifier import classify_query

# 검색 (RAG 및 웹 검색)
from rag_handler import search_with_fallback, perform_rag_search, perform_web_search
from map_handler import get_map_info

# LLM 및 응답 생성
from llm_generator import generate_response, rewrite_response, build_system_prompt

# 평가
from evaluation_controller import (
    evaluate_response,
    determine_next_action,
    collect_evaluation_metrics
)


# ==================== 색인 구축 워크플로우 ====================
def indexing_workflow(file_paths: List[str]) -> bool:
    """
    문서 색인 구축 워크플로우
    
    의료 문서를 벡터 DB에 인덱싱하는 별도의 워크플로우
    
    Args:
        file_paths (List[str]): 인덱싱할 문서 파일 경로 리스트
                               예: ["data/disease/001.json", "data/disease/002.json"]
        
    Returns:
        bool: 성공 여부 (True: 성공, False: 실패)
    
    처리 순서:
        1️⃣  [문서 수집] 파일 경로 리스트 입력
        2️⃣  [전처리] data_processor.batch_preprocess_documents()
            - 파일 로드 및 정제
            - 문서 청킹
            - 메타데이터 추출
        3️⃣  [임베딩] vector_store_manager.embed_and_index_chunks()
            - 각 청크를 벡터로 변환
            - 벡터 DB에 저장
        4️⃣  [검증] 저장 완료 확인
        5️⃣  [완료] 성공 여부 반환
    
    예시:
        ```python
        # 의료 문서 색인 구축
        success = indexing_workflow([
            "data/disease/disease_001.json",
            "data/disease/disease_002.json",
            "data/disease/disease_003.json"
        ])
        
        if success:
            print("✅ 색인 구축 완료!")
        else:
            print("❌ 색인 구축 실패")
        ```
    
    TODO:
        - data_processor.batch_preprocess_documents() 호출
        - 청크 수집 및 정제
        - vector_store_manager.embed_and_index_chunks() 호출
        - 오류 처리 및 검증
    """
    
    print(f"\n{'='*60}")
    print(f"📚 색인 구축 워크플로우 시작")
    print(f"{'='*60}\n")
    print(f"📄 처리할 문서: {len(file_paths)}개\n")
    
    start_time = time.time()
    
    # ==================== 스텝 1: 문서 전처리 ====================
    print("1️⃣  [스텝 1] 문서 전처리 및 청킹\n")
    
    processed_docs = batch_preprocess_documents(file_paths, chunk_size=500)
    
    # 모든 청크 수집
    all_chunks = []
    for doc_result in processed_docs:
        all_chunks.extend(doc_result['chunks'])
    
    print(f"✓ 전처리 완료: 총 {len(all_chunks)}개 청크 생성\n")
    
    # ==================== 스텝 2: 임베딩 및 인덱싱 ====================
    print("2️⃣  [스텝 2] 임베딩 및 벡터 DB 인덱싱\n")
    
    success = embed_and_index_chunks(all_chunks)
    
    # ==================== 스텝 3: 완료 ====================
    elapsed_time = time.time() - start_time
    
    print("="*60)
    if success:
        print("✅ 색인 구축 완료!")
        print(f"   - 총 처리 시간: {elapsed_time:.2f}초")
        print(f"   - 처리된 문서: {len(file_paths)}개")
        print(f"   - 생성된 청크: {len(all_chunks)}개")
    else:
        print("❌ 색인 구축 실패")
    print("="*60 + "\n")
    
    return success


# ==================== 쿼리 처리 워크플로우 ====================
def main_workflow(query: str, max_rewrite_attempts: int = 2) -> str:
    """
    사용자 쿼리를 입력받아 처리하고 최종 답변을 반환하는 메인 워크플로우
    
    Args:
        query (str): 사용자의 입력 쿼리
        max_rewrite_attempts (int): 최대 재작성 시도 횟수 (기본값: 2)
        
    Returns:
        str: 최종 답변 텍스트
        
    워크플로우 스텝:
        1️⃣  [입력 분류] input_classifier.classify_query()
            → "medical_consultation" / "map_search" / "general"
        
        2️⃣  [정보 검색] 분류 결과에 따라 선택:
            - medical/general: rag_handler.search_with_fallback()
            - map_search: map_handler.get_map_info()
        
        3️⃣  [프롬프트 구성] llm_generator.build_system_prompt()
            → 쿼리 타입별 시스템 프롬프트
        
        4️⃣  [LLM 응답 생성] llm_generator.generate_response()
            → 초기 답변 생성
        
        5️⃣  [평가 루프] evaluation_controller.evaluate_response()
            → 4개 차원 평가 (정확도, 명확성, 완전성, 안전성)
        
        6️⃣  [다음 액션 결정] evaluation_controller.determine_next_action()
            - "accept": 응답 승인 (점수 >= 0.75)
            - "rewrite": 피드백 반영 재작성 (0.50 <= 점수 < 0.75)
            - "escalate": 수동 개입 필요 (점수 < 0.50)
        
        7️⃣  [메트릭 수집] evaluation_controller.collect_evaluation_metrics()
            → 성능 통계 기록
        
        8️⃣  [최종 반환] 최종 답변 반환
    
    처리 경로별 로직:
        
        A. Medical Consultation (의료 상담):
            1. RAG 검색 (의료 문서 검색)
            2. LLM 응답 생성 (의료 전문가 프롬프트)
            3. 안전성 검증 (면책 조항, 응급 대응)
            4. 평가 및 최종화
        
        B. Map Search (지도/병원 검색):
            1. 지도 API 조회 (병원 정보)
            2. LLM으로 포맷팅 (검색 결과 정리)
            3. 평가 및 최종화
        
        C. General (일반 질문):
            1. 웹 검색 또는 일반 지식 사용
            2. LLM 응답 생성
            3. 평가 및 최종화
    
    평가 루프 흐름:
        ```
        초기 응답 생성
              ↓
        평가 (4개 차원)
              ↓
        점수 계산 (평균)
              ↓
        ┌─────────────┬──────────────┬────────────┐
        │             │              │            │
      ≥0.75       0.50~0.75      <0.50
        │             │              │
        ✅ ACCEPT   🔄 REWRITE    ⚠️ ESCALATE
        │      (최대 2회)          │
        │             │              │
        └──────────────────────────────┘
              ↓
        최종 답변 반환
        ```
    
    예시:
        ```python
        # 단일 쿼리 처리
        response = main_workflow("강아지 피부염 증상?")
        print(response)
        
        # 출력:
        # ============================================================
        # 🚀 메인 워크플로우 시작
        # ============================================================
        # 📝 사용자 쿼리: 강아지 피부염 증상?
        # ============================================================
        #
        # 📊 [스텝 1] 입력 쿼리 분류...
        #    ✓ 분류 결과: medical_consultation
        #
        # 🔍 [스텝 2] 정보 검색...
        #    ✓ RAG 검색 성공
        #    📚 컨텍스트 길이: 234 문자
        #
        # ...
        #
        # ✨ 최종 답변 반환
        # ============================================================
        # 강아지 피부염은 피부 표면의 염증으로...
        ```
    
    TODO:
        - 전체 워크플로우 흐름 구현
        - 에러 처리 (API 오류, 타임아웃)
        - 로깅 및 모니터링
    """
    
    print(f"\n{'='*60}")
    print(f"🚀 메인 워크플로우 시작")
    print(f"{'='*60}")
    print(f"📝 사용자 쿼리: {query}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # ==================== 스텝 1: 입력 분류 ====================
    print("📊 [스텝 1] 입력 쿼리 분류...")
    query_type = classify_query(query)
    print(f"   ✓ 분류 결과: {query_type}\n")
    
    # ==================== 스텝 2: 정보 검색 ====================
    print("🔍 [스텝 2] 정보 검색...")
    
    if query_type == "map_search":
        # 지도 검색 처리
        context = get_map_info(query)
        search_source = "map_api"
        print(f"   ✓ 지도 API에서 병원 정보 조회 완료")
    else:
        # RAG/웹 검색
        context, search_source = search_with_fallback(query)
        if search_source == "rag":
            print(f"   ✓ RAG 검색 성공")
        else:
            print(f"   ✓ RAG 검색 실패 → 웹 검색으로 폴백")
    
    print(f"   📚 컨텍스트 길이: {len(context)} 문자\n")
    
    # ==================== 스텝 3: 시스템 프롬프트 구성 ====================
    print("💡 [스텝 3] 시스템 프롬프트 구성...")
    system_prompt = build_system_prompt(query_type)
    print(f"   ✓ 프롬프트 구성 완료\n")
    
    # ==================== 스텝 4: LLM 응답 생성 ====================
    print("🤖 [스텝 4] LLM 응답 생성...")
    response = generate_response(query, context)
    print(f"   ✓ 초기 응답 생성 완료")
    print(f"   📄 응답 길이: {len(response)} 문자\n")
    
    # ==================== 스텝 5: 평가 및 재작성 루프 ====================
    print("⚖️  [스텝 5] 응답 평가 및 재작성 루프...\n")
    
    rewrite_count = 0
    while rewrite_count <= max_rewrite_attempts:
        
        # 응답 평가
        evaluation = evaluate_response(response)
        avg_score = evaluation.get('average_score', 0)
        
        # 다음 액션 결정
        next_action = determine_next_action(response, evaluation)
        
        if next_action == "accept":
            print(f"   ✅ 평가 통과! 응답 승인\n")
            break
        elif next_action == "rewrite" and rewrite_count < max_rewrite_attempts:
            print(f"   🔄 응답 재작성 필요 (시도 #{rewrite_count + 1}/{max_rewrite_attempts})")
            response = rewrite_response(response, evaluation['feedback'])
            rewrite_count += 1
        else:
            print(f"   ⚠️  최대 재작성 횟수 초과 또는 에스컬레이션 필요\n")
            break
    
    # ==================== 스텝 6: 메트릭 수집 및 로깅 ====================
    generation_time = time.time() - start_time
    metrics = collect_evaluation_metrics(
        response,
        evaluation,
        generation_time,
        rewrite_count
    )
    
    print("\n📈 [스텝 6] 최종 메트릭:")
    print(f"   - 총 처리 시간: {generation_time:.2f}초")
    print(f"   - 재작성 횟수: {rewrite_count}회")
    print(f"   - 최종 평가 점수: {metrics['average_score']:.2%}")
    print(f"   - 평가 통과: {'✓' if metrics['passed_evaluation'] else '✗'}\n")
    
    # ==================== 최종 답변 반환 ====================
    print(f"{'='*60}")
    print(f"✨ 최종 답변 반환")
    print(f"{'='*60}\n")
    
    return response


def main_workflow_with_feedback(
    query: str,
    user_feedback: str,
    max_rewrite_attempts: int = 2
) -> str:
    """
    사용자 피드백을 포함한 확장 워크플로우
    
    Args:
        query (str): 사용자 쿼리
        user_feedback (str): 사용자 피드백 (예: "더 짧게", "더 쉽게")
        max_rewrite_attempts (int): 최대 재작성 횟수
        
    Returns:
        str: 피드백 반영 최종 답변
        
    추가 기능:
        - 사용자 피드백 적용
        - 대화형 개선
        - 반복적 정제
    
    TODO:
        - 초기 응답 생성
        - 피드백 반영 재작성
        - 최종 평가
    """
    
    print(f"\n🔄 피드백 기반 워크플로우 시작")
    print(f"사용자 피드백: {user_feedback}\n")
    
    # 초기 응답 생성
    initial_response = main_workflow(query, max_rewrite_attempts=1)
    
    # 피드백 반영 재작성
    refined_response = rewrite_response(initial_response, user_feedback)
    
    # 최종 평가
    final_evaluation = evaluate_response(refined_response)
    
    print(f"\n피드백 반영 최종 평가 점수: {final_evaluation.get('average_score', 0):.2%}")
    
    return refined_response


def batch_workflow(queries: List[str]) -> List[Dict[str, any]]:
    """
    여러 쿼리를 배치 처리
    
    Args:
        queries (List[str]): 처리할 쿼리 리스트
        
    Returns:
        list[Dict[str, any]]: 각 쿼리의 처리 결과
            [
                {
                    'query': str,
                    'response': str,
                    'query_type': str,
                    'processing_time': float,
                    'evaluation_score': float
                },
                ...
            ]
    
    예시:
        ```python
        queries = [
            "강아지 피부염 증상?",
            "서울 강남역 근처 병원",
            "반려동물 보험은?"
        ]
        
        results = batch_workflow(queries)
        
        for result in results:
            print(f"쿼리: {result['query']}")
            print(f"타입: {result['query_type']}")
            print(f"점수: {result['evaluation_score']:.0%}\n")
        ```
    
    TODO:
        - 배치 처리 로직
        - 병렬 처리 또는 순차 처리
        - 통계 수집
        - 결과 저장
    """
    
    results = []
    
    print(f"\n🔁 배치 워크플로우 시작")
    print(f"총 {len(queries)}개 쿼리 처리\n")
    
    for idx, query in enumerate(queries, 1):
        print(f"[{idx}/{len(queries)}] 처리 중: {query}")
        
        start_time = time.time()
        response = main_workflow(query, max_rewrite_attempts=1)
        processing_time = time.time() - start_time
        
        # 최종 평가 점수 수집
        evaluation = evaluate_response(response)
        
        result = {
            'query': query,
            'response': response,
            'query_type': classify_query(query),
            'processing_time': processing_time,
            'evaluation_score': evaluation.get('average_score', 0)
        }
        
        results.append(result)
    
    # 통계 출력
    avg_time = sum(r['processing_time'] for r in results) / len(results) if results else 0
    avg_score = sum(r['evaluation_score'] for r in results) / len(results) if results else 0
    
    print(f"\n📊 배치 처리 완료")
    print(f"   - 평균 처리 시간: {avg_time:.2f}초")
    print(f"   - 평균 평가 점수: {avg_score:.2%}")
    
    return results


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """
    테스트 실행 (스켈레톤 데모)
    """
    
    print("\n" + "="*60)
    print("🏥 RAG 기반 AI 어시스턴트 - 8개 모듈 스켈레톤 코드")
    print("="*60)
    
    # 테스트 쿼리들
    test_queries = [
        "강아지 피부 질환 증상이 뭐예요?",
        "서울 강남역 근처 24시간 동물병원 찾아줘",
        "반려동물 예방 접종은 언제 해야 하나요?"
    ]
    
    # 1️⃣ 색인 구축 워크플로우
    print("\n\n### 테스트 1: 색인 구축 워크플로우 ###\n")
    
    # 샘플 파일 경로 (실제로는 data/ 디렉토리의 파일들)
    sample_files = [
        "data/disease/disease_001.json",
        "data/disease/disease_002.json"
    ]
    
    indexing_success = indexing_workflow(sample_files)
    
    # 2️⃣ 단일 쿼리 처리
    print("\n\n### 테스트 2: 단일 쿼리 처리 ###\n")
    single_response = main_workflow(test_queries[0])
    print(f"\n최종 답변:\n{single_response}")
    
    # 3️⃣ 배치 처리
    print("\n\n### 테스트 3: 배치 처리 ###\n")
    batch_results = batch_workflow(test_queries[:2])
    
    for result in batch_results:
        print(f"\n쿼리: {result['query']}")
        print(f"분류: {result['query_type']}")
        print(f"점수: {result['evaluation_score']:.2%}")
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)
