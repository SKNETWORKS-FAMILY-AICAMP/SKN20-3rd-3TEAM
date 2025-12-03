"""
통합 실행 스크립트 (최적화 버전)
- 캐싱 시스템 (Vector DB + pkl)
- 키워드 추출 (Query Re-writing)
- 불용어 제거
- 청크 사이즈 최적화 (512 토큰)
- 상대 경로 관리
"""

import os
import sys
from dotenv import load_dotenv

# src 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.preprocessing import load_and_preprocess_data, load_multiple_departments
from rag.pipeline import setup_rag_pipeline, query_rag
from agent.workflow import run_agent

# 최적화 모듈 import
try:
    from utils.optimization import manage_persistence, get_project_path
    OPTIMIZATION_ENABLED = True
    print("✅ 최적화 모듈 로드 완료 (캐싱, 키워드 추출 활성화)")
except ImportError:
    OPTIMIZATION_ENABLED = False
    print("⚠️ 최적화 모듈 없음 - 기본 모드로 실행")

# instruction 추출 함수
def extract_system_instruction(labeled_documents):
    """
    라벨링 데이터에서 instruction을 추출하여 System Prompt에 활용
    
    Args:
        labeled_documents: 라벨링 데이터 Document 리스트
        
    Returns:
        대표 instruction 문자열
    """
    instructions = []
    for doc in labeled_documents:
        if doc.metadata.get('data_type') == 'labeled':
            instruction = doc.metadata.get('instruction', '')
            if instruction and instruction not in instructions:
                instructions.append(instruction)
    
    # 가장 포괄적인 instruction 반환 (또는 첫 번째)
    return instructions[0] if instructions else ""


def main():
    """메인 실행 함수 (최적화 버전)"""
    
    # 전역 변수 사용 선언
    global OPTIMIZATION_ENABLED
    
    # 환경 변수 로드
    load_dotenv()
    
    print("="*80)
    print("🐾 반려동물 건강 상담 챗봇 시스템 (최적화 버전)")
    print("="*80)
    
    # ========================================================================
    # 경로 설정 (상대 경로 사용)
    # ========================================================================
    if OPTIMIZATION_ENABLED:
        # 최적화 모듈의 경로 관리 사용
        source_base_path = get_project_path(
            'data', 
            '59.반려견 성장 및 질병 관련 말뭉치 데이터',
            '3.개방데이터',
            '1.데이터',
            'Training',
            '01.원천데이터'
        )
        persist_dir = get_project_path('data', 'chroma_db')
        print(f"📂 상대 경로 관리 활성화")
        print(f"   - 데이터: {source_base_path}")
        print(f"   - Vector DB: {persist_dir}")
    else:
        # 기존 방식 (절대 경로)
        source_base_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training\01.원천데이터"
        persist_dir = "./chroma_db"
    
    # ========================================================================
    # 1단계: 캐싱 시스템을 통한 RAG 초기화
    # ========================================================================
    print("\n[1단계] RAG 시스템 초기화 중...")
    
    if OPTIMIZATION_ENABLED:
        print("🚀 최적화 모드: 캐싱 시스템 활성화")
        print("   - Vector DB 존재 → 즉시 로드 (~5초)")
        print("   - pkl 존재 → 임베딩만 수행 (~2분)")
        print("   - 없음 → 전체 재구축 (~8분)")
        
        try:
            rag_result = manage_persistence(
                data_path=source_base_path,
                persist_dir=persist_dir,
                force_rebuild=False  # True로 변경하면 강제 재구축
            )
            
            retriever = rag_result["retriever"]
            vectorstore = rag_result["vectorstore"]
            status = rag_result["status"]
            
            print(f"\n✅ RAG 시스템 준비 완료 (상태: {status})")
            
            # RAG 컴포넌트 구성 (기존 코드 호환)
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.runnables import RunnablePassthrough
            
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            
            # 간단한 RAG 체인 구성
            from rag.pipeline import VETERINARY_EXPERT_SYSTEM_PROMPT
            prompt = ChatPromptTemplate.from_template(VETERINARY_EXPERT_SYSTEM_PROMPT)
            
            def format_docs(docs):
                formatted = []
                for i, doc in enumerate(docs, 1):
                    dept = doc.metadata.get('department', '알 수 없음')
                    title = doc.metadata.get('title', '제목 없음')
                    formatted.append(f"[문서 {i} - {dept}과]\n{doc.page_content}\n")
                return "\n".join(formatted)
            
            rag_chain = (
                {"context": retriever | format_docs, "input": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            rag_components = {
                "chain": rag_chain,
                "retriever": retriever,
                "vectorstore": vectorstore,
                "llm": llm
            }
            
        except Exception as e:
            print(f"⚠️ 최적화 모드 실패: {e}")
            print("   기본 모드로 전환합니다...")
            OPTIMIZATION_ENABLED = False
    
    if not OPTIMIZATION_ENABLED:
        # 기본 모드: 기존 방식대로 실행
        print("📊 기본 모드: 데이터 로드 및 전처리")
        
        labeled_base_path = source_base_path.replace("01.원천데이터", "02.라벨링데이터")
        
        # 원천 데이터 로드 (최적화된 청크 설정 자동 적용)
        print("\n[1-1] 원천 데이터 로드 중...")
        source_documents = load_multiple_departments(
            base_path=source_base_path,
            departments=["내과", "외과", "안과", "치과", "피부과"],
            data_type="source",
            chunk_size=None,  # None이면 최적화된 512 사용
            chunk_overlap=None,  # None이면 최적화된 80 사용
            remove_stopwords=True  # 불용어 제거 활성화
        )
        
        # 라벨링 데이터 로드
        print("\n[1-2] 라벨링 데이터 로드 중...")
        labeled_documents = load_multiple_departments(
            base_path=labeled_base_path,
            departments=["내과", "외과", "안과", "치과", "피부과"],
            data_type="labeled",
            chunk_size=None,
            chunk_overlap=None,
            remove_stopwords=True
        )
        
        all_documents = source_documents + labeled_documents
        
        if not all_documents:
            print("⚠️ 문서를 로드할 수 없습니다. 데이터 경로를 확인하세요.")
            return
        
        print(f"\n✓ 원천 데이터: {len(source_documents)}개 청크")
        print(f"✓ 라벨링 데이터: {len(labeled_documents)}개 청크")
        print(f"✓ 총 {len(all_documents)}개의 문서 청크 로드 완료")
        
        # RAG 파이프라인 구축
        print("\n[2단계] RAG 파이프라인 구축 중...")
        rag_components = setup_rag_pipeline(
            documents=all_documents,
            embedding_model="text-embedding-3-small",
            model_name="gpt-4o-mini",
            persist_directory=persist_dir,
            use_existing_vectorstore=False,
            k=4
        )
        
        print("✓ RAG 파이프라인 구축 완료")
    
    # ========================================================================
    # 2단계: RAG 파이프라인 테스트 (키워드 추출 적용)
    # ========================================================================
    print("\n[2단계] RAG 파이프라인 테스트...")
    
    test_query = "강아지가 구토를 하고 황달 증상이 있습니다. 어떤 질환일까요?"
    print(f"\n테스트 질문: {test_query}")
    
    # 키워드 추출 적용 (최적화 모드)
    if OPTIMIZATION_ENABLED:
        from utils.optimization import extract_keywords_for_query
        from langchain_openai import ChatOpenAI
        
        llm_temp = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        optimized_query = extract_keywords_for_query(test_query, llm_temp)
        print(f"🔑 최적화된 쿼리: {optimized_query}")
        test_query_final = optimized_query
    else:
        test_query_final = test_query
    
    answer = query_rag(rag_components["chain"], test_query_final)
    print(f"\nRAG 답변:\n{answer}")
    
    # ========================================================================
    # 3단계: LangGraph Agent 실행 (최적화 워크플로우)
    # ========================================================================
    print("\n\n" + "="*80)
    print("[3단계] LangGraph Agent 워크플로우 실행")
    print("="*80)
    print("🔍 키워드 추출: 활성화" if OPTIMIZATION_ENABLED else "")
    print("🔍 의학적 검수: 활성화 (최대 2회 재검토)")
    print("📐 최적화된 청크: 512 토큰")
    print("="*80)
    
    # Agent 테스트 케이스 (기대 응급도 포함) - 10개
    agent_test_cases = [
        # 응급도 높음 - 생명 위협 증상
        {
            "query": "저희 강아지가 갑자기 구토를 여러 번 하고 배가 부풀어 올랐어요. 매우 아파 보입니다.",
            "expected_urgency": "높음",
            "reason": "위 확장/비틀림 의심, 생명 위협"
        },
        {
            "query": "강아지가 호흡이 거칠고 입술이 파래졌어요. 계속 헐떡이고 있습니다.",
            "expected_urgency": "높음",
            "reason": "청색증, 호흡곤란, 즉각 치료 필요"
        },
        {
            "query": "강아지가 발작을 일으키고 의식을 잃었어요. 30초 정도 지속됐습니다.",
            "expected_urgency": "높음",
            "reason": "발작, 신경계 응급상황"
        },
        
        # 응급도 보통 - 며칠 내 진료 필요
        {
            "query": "고양이 눈이 약간 충혈되었는데 평소와 다를 게 없어요.",
            "expected_urgency": "보통",
            "reason": "경미한 안과 증상, 1-2일 내 진료"
        },
        {
            "query": "강아지가 어제부터 가끔씩 기침을 합니다. 컨디션은 괜찮은 것 같아요.",
            "expected_urgency": "보통",
            "reason": "호흡기 증상, 2-3일 내 검진 권장"
        },
        {
            "query": "반려견이 오른쪽 귀를 자주 긁고 머리를 흔들어요. 귓속이 좀 붉어 보입니다.",
            "expected_urgency": "보통",
            "reason": "외이도염 의심, 일주일 내 진료"
        },
        {
            "query": "강아지 배 쪽에 붉은 반점이 생겼고 가려워하는 것 같아요.",
            "expected_urgency": "보통",
            "reason": "피부 염증/알레르기, 일주일 내 진료"
        },
        
        # 응급도 낮음 - 경미한 증상
        {
            "query": "강아지 발톱이 너무 길어진 것 같은데 언제 병원 가야 할까요?",
            "expected_urgency": "낮음",
            "reason": "일상 관리, 비응급"
        },
        {
            "query": "고양이가 평소보다 물을 조금 더 많이 마시는 것 같아요. 다른 증상은 없습니다.",
            "expected_urgency": "낮음",
            "reason": "경미한 변화, 관찰 후 판단"
        },
        {
            "query": "강아지 입에서 냄새가 나는데 밥은 잘 먹어요. 치석이 좀 있는 것 같습니다.",
            "expected_urgency": "보통",
            "reason": "치석/치주질환, 스케일링 필요"
        },
    ]
    
    for i, test_case in enumerate(agent_test_cases, 1):
        query = test_case["query"]
        expected_urgency = test_case["expected_urgency"]
        reason = test_case["reason"]
        
        print(f"\n\n{'─'*80}")
        print(f"Agent 테스트 {i}: {query}")
        print(f"기대 응급도: {expected_urgency} ({reason})")
        print('─'*80)
        
        result = run_agent(
            user_query=query,
            config={"configurable": {"thread_id": f"test_{i}"}}
        )
        
        # 결과 출력
        print("\n" + "┌" + "─"*78 + "┐")
        print("│ 최종 응답" + " "*68 + "│")
        print("└" + "─"*78 + "┘")
        print(result.get("final_response", "응답 생성 실패"))
        
        # 판단 결과 및 정확도 표시
        actual_urgency = result.get('urgency_level', 'N/A')
        is_correct = actual_urgency == expected_urgency
        correctness = "✅ 정답" if is_correct else "❌ 오답"
        
        print("\n" + "┌" + "─"*78 + "┐")
        print(f"│ 판단 결과" + " "*66 + "│")
        print("└" + "─"*78 + "┘")
        print(f"기대 응급도: {expected_urgency} | 실제 응급도: {actual_urgency} | {correctness}")
        print(f"추천 진료과: {result.get('recommended_department', 'N/A')}")
        
        if result.get("hospital_list"):
            print(f"추천 병원 수: {len(result['hospital_list'])}개")
    
    # ========================================================================
    # 완료
    # ========================================================================
    print("\n\n" + "="*80)
    print("✅ 모든 테스트가 완료되었습니다!")
    print("="*80)
    
    if OPTIMIZATION_ENABLED:
        print("\n🚀 적용된 최적화:")
        print("  ✅ 캐싱 시스템 (Vector DB + pkl)")
        print("  ✅ 키워드 추출 (Query Re-writing)")
        print("  ✅ 불용어 제거 (KoNLPy)")
        print("  ✅ 청크 최적화 (512 토큰)")
        print("  ✅ 의학적 검수 (피드백 루프)")
        print("  ✅ 상대 경로 관리")
        print("\n💡 다음 실행 시 Vector DB 캐시 사용으로 ~5초 만에 시작됩니다!")
    
    print("\n📝 다음 단계:")
    print("1. 카카오맵 API 연동하여 실제 병원 검색 구현")
    print("2. 웹 인터페이스 또는 챗봇 UI 개발 (Streamlit/Gradio)")
    print("3. 사용자 피드백 수집 및 모델 개선")
    print("4. 멀티턴 대화 기능 추가")


if __name__ == "__main__":
    main()
