"""
통합 실행 스크립트
전체 파이프라인을 한 번에 실행하는 메인 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# src 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.preprocessing import load_and_preprocess_data, load_multiple_departments
from rag.pipeline import setup_rag_pipeline, query_rag
from agent.workflow import run_agent

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
    """메인 실행 함수"""
    
    # 환경 변수 로드
    load_dotenv()
    
    print("="*80)
    print("반려동물 건강 상담 챗봇 시스템")
    print("="*80)
    
    # ========================================================================
    # 1단계: 데이터 로드 및 전처리
    # ========================================================================
    print("\n[1단계] 데이터 로드 및 전처리 중...")
    
    # 데이터 경로 설정
    base_data_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training"
    source_base_path = os.path.join(base_data_path, "01.원천데이터")
    labeled_base_path = os.path.join(base_data_path, "02.라벨링데이터")
    
    # 원천 데이터 로드 (RAG 지식 베이스용 - disease 텍스트 임베딩)
    print("\n[1-1] 원천 데이터 로드 중 (RAG 지식 베이스용)...")
    source_documents = load_multiple_departments(
        base_path=source_base_path,
        departments=["내과", "외과", "안과", "치과", "피부과"],
        data_type="source",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # 라벨링 데이터 로드 (QA 패턴 학습 및 instruction 참고용)
    print("\n[1-2] 라벨링 데이터 로드 중 (QA 패턴 및 instruction 참고용)...")
    labeled_documents = load_multiple_departments(
        base_path=labeled_base_path,
        departments=["내과", "외과", "안과", "치과", "피부과"],
        data_type="labeled",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # 두 데이터 합치기 (RAG Vector Store에 모두 포함)
    all_documents = source_documents + labeled_documents
    
    if not all_documents:
        print("⚠️ 문서를 로드할 수 없습니다. 데이터 경로를 확인하세요.")
        return
    
    print(f"\n✓ 원천 데이터: {len(source_documents)}개 청크")
    print(f"✓ 라벨링 데이터: {len(labeled_documents)}개 청크")
    print(f"✓ 총 {len(all_documents)}개의 문서 청크 로드 완료")
    
    # 라벨링 데이터에서 instruction 추출 (지침 4.2: System Prompt에 활용)
    system_instruction = extract_system_instruction(labeled_documents)
    if system_instruction:
        print(f"\n✓ System Instruction 추출 완료: {system_instruction[:100]}...")
    
    # ========================================================================
    # 2단계: RAG 파이프라인 구축
    # ========================================================================
    print("\n[2단계] RAG 파이프라인 구축 중...")
    print("- 원천 데이터: disease 텍스트 기반 임베딩 (지식 베이스)")
    print("- 라벨링 데이터: QA 쌍 기반 임베딩 (질문 패턴 학습)")
    print("- 메타데이터: department, urgency, lifeCycle 등 필터링용")
    
    rag_components = setup_rag_pipeline(
        documents=all_documents,  # 원천 + 라벨링 데이터 모두 사용
        embedding_model="text-embedding-3-small",
        model_name="gpt-4o-mini",
        persist_directory="./chroma_db",
        use_existing_vectorstore=False,  # 첫 실행 시 False, 이후 True로 변경 가능
        k=4
    )
    
    print("✓ RAG 파이프라인 구축 완료")
    
    # ========================================================================
    # 3단계: RAG 파이프라인 테스트
    # ========================================================================
    print("\n[3단계] RAG 파이프라인 테스트...")
    
    test_query = "강아지가 구토를 하고 황달 증상이 있습니다. 어떤 질환일까요?"
    print(f"\n테스트 질문: {test_query}")
    
    answer = query_rag(rag_components["chain"], test_query)
    print(f"\nRAG 답변:\n{answer}")
    
    # ========================================================================
    # 4단계: LangGraph Agent 실행 (통합 워크플로우)
    # ========================================================================
    print("\n\n" + "="*80)
    print("[4단계] LangGraph Agent 워크플로우 실행")
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
    print("모든 테스트가 완료되었습니다!")
    print("="*80)
    
    print("\n📝 다음 단계:")
    print("1. 실제 데이터 경로로 변경하여 전체 데이터 로드")
    print("2. 카카오맵 API 연동하여 실제 병원 검색 구현")
    print("3. 웹 인터페이스 또는 챗봇 UI 개발")
    print("4. 사용자 피드백 수집 및 모델 개선")


if __name__ == "__main__":
    main()
