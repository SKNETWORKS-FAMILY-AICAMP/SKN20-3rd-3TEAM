"""
RAG Handler Module
RAG(Retrieval-Augmented Generation) 및 웹 검색 처리

역할:
  - 벡터 DB를 활용한 RAG 검색
  - 웹 검색 API 통합
  - CRAG 패턴 구현 (검색 실패 시 웹 검색 폴백)
"""

from typing import Tuple, Optional


def perform_rag_search(query: str) -> str:
    """
    RAG 시스템을 통해 벡터 DB에서 관련 문서 검색
    
    Args:
        query (str): 검색할 쿼리
        
    Returns:
        str: 검색된 컨텍스트 문서 텍스트
            빈 문자열이면 검색 실패 (웹 검색으로 폴백)
        
    처리 순서:
        1️⃣  [쿼리 임베딩] 검색 쿼리를 벡터로 변환
        2️⃣  [벡터 검색] 벡터 DB (Chroma)에서 유사 문서 검색 (Top-K=5)
        3️⃣  [관련성 평가] LLM을 사용한 문서 관련성 평가 (Grading)
        4️⃣  [필터링] 임계값 이상의 관련 문서만 선별
        5️⃣  [문서 반환] 필터링된 문서 텍스트 병합하여 반환
    
    CRAG 패턴의 일부:
        - 이 함수가 비어있거나 점수가 낮으면 웹 검색으로 전환
        - perform_web_search()로 폴백
    
    TODO:
        - VectorStoreManager의 search_similar_chunks() 호출
        - 문서 관련성 평가 (LLM 또는 휴리스틱)
        - 임계값 필터링
        - 최종 컨텍스트 생성
    """
    # TODO: RAG 파이프라인 호출
    # 1. vector_manager = get_vector_manager()
    # 2. results = vector_manager.search_similar_chunks(query, top_k=5)
    # 3. 결과 필터링 및 평가
    # 4. 최종 컨텍스트 생성
    
    # 더미 응답
    context = f"[RAG 검색 결과]\n쿼리: {query}\n\n관련 문서 내용:\n- 강아지 질환 관련 정보\n- 증상 설명\n- 치료 방법"
    print(f"✓ [perform_rag_search] '{query}' → RAG 검색 성공 ({len(context)} 문자)")
    return context


def perform_web_search(query: str) -> str:
    """
    웹 검색을 통해 실시간 정보 검색
    
    Args:
        query (str): 검색할 쿼리
        
    Returns:
        str: 웹 검색 결과 컨텍스트 텍스트
        
    처리 순서:
        1️⃣  [검색 쿼리 구성] 검색 엔진 최적화 쿼리 생성
        2️⃣  [API 호출] Tavily 또는 Google Search API 호출
        3️⃣  [결과 수집] 상위 K개 검색 결과 추출
        4️⃣  [텍스트 추출] 검색 결과를 구조화된 텍스트로 변환
        5️⃣  [최종 반환] 컨텍스트 생성
    
    사용 시점:
        - RAG 검색에서 관련 문서 없음
        - 실시간 정보 필요 (병원 영업 시간, 뉴스 등)
        - 동적 정보 필요
    
    TODO:
        - Tavily API 호출
        - 검색 결과 파싱
        - 텍스트 추출 및 정제
    """
    # TODO: 웹 검색 API 호출
    # - client = TavilyClient(api_key=TAVILY_API_KEY)
    # - results = client.search(query, max_results=5)
    
    # 더미 응답
    web_results = f"[웹 검색 결과]\n쿼리: {query}\n\n검색 결과:\n- 인터넷에서 찾은 관련 정보\n- 최신 뉴스\n- 참고 자료"
    print(f"✓ [perform_web_search] '{query}' → 웹 검색 성공 ({len(web_results)} 문자)")
    return web_results


def search_with_fallback(query: str) -> Tuple[str, str]:
    """
    RAG 검색 실패 시 웹 검색으로 자동 폴백하는 통합 검색 함수
    
    Args:
        query (str): 검색할 쿼리
        
    Returns:
        Tuple[str, str]: (검색_결과, 검색_소스)
            - 검색_결과: 컨텍스트 텍스트
            - 검색_소스: "rag" 또는 "web"
        
    CRAG 패턴 구현 (Corrective RAG):
        1. 먼저 RAG 검색 시도
        2. 관련 문서 충분 → RAG 결과 반환 (source="rag")
        3. 관련 문서 부족 → 웹 검색 자동 전환 (source="web")
        4. 최종 컨텍스트 반환
    
    처리 흐름:
        ```
        쿼리
          ↓
        [RAG 검색]
          ↓
        관련 문서 있나?
          ├─ YES → RAG 결과 반환, source="rag"
          ├─ NO → [웹 검색]
          │       웹 검색 결과 반환, source="web"
          └─
        ```
    
    TODO:
        - RAG 검색 수행
        - 결과 검증 (문서 관련성, 길이 확인)
        - 폴백 조건 정의
        - 웹 검색으로 전환
    """
    # TODO: CRAG (Corrective RAG) 로직 구현
    
    print(f"\n🔍 [search_with_fallback] 통합 검색 시작: '{query}'\n")
    
    # Step 1: RAG 검색 시도
    print("  1️⃣  RAG 검색 시도...")
    rag_result = perform_rag_search(query)
    
    # Step 2: 관련 문서 충분성 판단
    if rag_result and len(rag_result) > 100:
        # RAG 검색 성공
        print("  2️⃣  관련 문서 충분 → RAG 결과 사용")
        print(f"  ✓ 검색 소스: rag\n")
        return rag_result, "rag"
    else:
        # RAG 검색 실패 → 웹 검색으로 폴백
        print("  2️⃣  관련 문서 부족 → 웹 검색으로 폴백")
        print("  3️⃣  웹 검색 수행...")
        web_result = perform_web_search(query)
        print(f"  ✓ 검색 소스: web\n")
        return web_result, "web"


def grade_documents(
    query: str,
    documents: list[str],
    threshold: float = 0.5
) -> list[Tuple[str, float]]:
    """
    검색된 문서의 관련성을 평가하고 필터링
    
    Args:
        query (str): 원본 검색 쿼리
        documents (list[str]): 평가할 문서 리스트
        threshold (float): 관련성 임계값 (0.0-1.0)
        
    Returns:
        list[Tuple[str, float]]: [(문서, 관련성_점수), ...]
            관련성_점수: 0.0 (무관) ~ 1.0 (매우 관련)
    
    평가 기준:
        - 문서가 쿼리의 주제를 다루는가?
        - 문서의 정확도는?
        - 문서의 신뢰도는?
    
    TODO:
        - LLM 기반 관련성 평가
        - 휴리스틱 기반 평가 (키워드 매칭)
    """
    # TODO: 문서 관련성 평가 로직
    
    print(f"⚖️  [grade_documents] {len(documents)}개 문서 평가 (임계값: {threshold})")
    
    # 더미 평가
    graded = [(doc, 0.85) for doc in documents]
    
    return graded


def format_context(
    documents: list[str],
    source: str = "unknown"
) -> str:
    """
    여러 문서를 단일 컨텍스트 문자열로 포맷팅
    
    Args:
        documents (list[str]): 문서 리스트
        source (str): 검색 소스 ("rag", "web", "hybrid")
        
    Returns:
        str: 포맷된 컨텍스트 텍스트
        
    포맷:
        ```
        [검색 결과 - RAG]
        
        문서 1:
        ...
        
        문서 2:
        ...
        ```
    
    TODO:
        - 문서 순서 정렬
        - 중복 제거
        - 메타데이터 추가
    """
    # TODO: 포맷팅 로직
    
    context = f"[검색 결과 - {source.upper()}]\n\n"
    for idx, doc in enumerate(documents, 1):
        context += f"[문서 {idx}]\n{doc}\n\n"
    
    return context


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """
    테스트 실행 (스켈레톤 데모)
    """
    
    print("\n" + "="*60)
    print("🔍 RAG Handler Module - 테스트")
    print("="*60)
    
    test_query = "강아지 피부 질환 증상"
    
    print("\n### 테스트 1: RAG 검색 ###\n")
    rag_result = perform_rag_search(test_query)
    print(f"결과: {rag_result[:100]}...\n")
    
    print("\n### 테스트 2: 웹 검색 ###\n")
    web_result = perform_web_search(test_query)
    print(f"결과: {web_result[:100]}...\n")
    
    print("\n### 테스트 3: 폴백 검색 ###\n")
    fallback_result, source = search_with_fallback(test_query)
    print(f"소스: {source}")
    print(f"결과: {fallback_result[:100]}...\n")
    
    print("\n### 테스트 4: 문서 평가 ###\n")
    test_docs = ["문서1", "문서2"]
    graded = grade_documents(test_query, test_docs)
    print(f"평가 결과: {graded}\n")
    
    print("="*60)
    print("✅ 테스트 완료!")
    print("="*60)

