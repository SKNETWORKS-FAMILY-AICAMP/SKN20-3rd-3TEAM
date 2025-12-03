"""
LangGraph Agent 워크플로우 - 기본 버전
증상 분석 → 응급도 판단 → 병원 추천 자동화 워크플로우
"""

import os
import sys
from typing import TypedDict, Literal, Dict, Any, List
from typing_extensions import TypedDict

# 상위 디렉토리 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from utils.tools import rag_search_tool, hospital_recommend_tool


# ============================================================================
# 상태 정의 (State Schema)
# ============================================================================

class AgentState(TypedDict):
    """Agent의 상태를 정의하는 TypedDict"""
    messages: List[Any]  # 대화 히스토리
    user_query: str  # 사용자 원본 질문
    symptoms_analysis: str  # 증상 분석 결과
    urgency_level: str  # 응급도 수준 ("높음", "보통", "낮음")
    recommended_department: str  # 추천 진료과
    hospital_list: List[Dict[str, str]]  # 추천 병원 리스트
    final_response: str  # 최종 응답
    next_action: str  # 다음 액션 지시


# ============================================================================
# Node 함수 정의
# ============================================================================

def analyze_symptom_node(state: AgentState) -> AgentState:
    """
    Node 1: 증상 분석 (RAG 검색 수행) - 지침 4.2: lifeCycle 추론 및 활용
    
    사용자의 질문을 분석하고 RAG를 통해 관련 정보를 검색합니다.
    """
    print("\n[Node 1] 증상 분석 시작...")
    
    user_query = state["user_query"]
    
    # lifeCycle 추론 (지침 4.2: 질문 속성 부여)
    life_cycle = _infer_life_cycle(user_query)
    
    # 진료과 추론 (키워드 기반)
    department_hint = _infer_department(user_query)
    
    # RAG 검색 수행 (lifeCycle 정보 포함)
    search_query = user_query
    if life_cycle:
        search_query = f"[{life_cycle}] {user_query}"
    
    rag_result = rag_search_tool.invoke({
        "query": search_query, 
        "department": department_hint
    })
    
    # 상태 업데이트
    analysis_with_context = f"""[환자 정보: {life_cycle or '연령 미상'}]

{rag_result}

※ 이 분석은 {life_cycle or '연령대 불명'}인 반려동물을 고려하여 작성되었습니다."""
    
    state["symptoms_analysis"] = analysis_with_context
    state["messages"].append(AIMessage(content=f"증상 분석 완료:\n{analysis_with_context}"))
    
    print(f"[Node 1 완료] 분석 결과 저장됨 (lifeCycle: {life_cycle})")
    
    return state


def _infer_life_cycle(query: str) -> str:
    """
    질문에서 lifeCycle 추론 (지침 4.2)
    
    Args:
        query: 사용자 질문
        
    Returns:
        추론된 lifeCycle (자견/성견/노령견 등)
    """
    query_lower = query.lower()
    
    if any(keyword in query for keyword in ['강아지', '자견', '새끼', '어린', '생후']):
        return '자견'
    elif any(keyword in query for keyword in ['노령', '노견', '늙은', '나이든', '시니어']):
        return '노령견'
    elif any(keyword in query for keyword in ['성견', '성인']):
        return '성견'
    
    return ''  # 추론 불가


def _infer_department(query: str) -> str:
    """
    질문에서 진료과 추론 (키워드 기반)
    
    Args:
        query: 사용자 질문
        
    Returns:
        추론된 진료과
    """
    department_keywords = {
        '안과': ['눈', '시력', '충혈', '각막', '결막', '백내장'],
        '치과': ['이', '치아', '잇몸', '치석', '구취', '입냄새'],
        '피부과': ['피부', '가려움', '탈모', '붉은', '발진', '반점'],
        '외과': ['골절', '상처', '수술', '외상', '절단'],
        '내과': ['구토', '설사', '기침', '황달', '발열']
    }
    
    for dept, keywords in department_keywords.items():
        if any(keyword in query for keyword in keywords):
            return dept
    
    return ''  # 진료과 추론 불가


def triage_and_decide_node(state: AgentState) -> AgentState:
    """
    Node 2: 응급도 판단 및 다음 단계 결정 (지침 5: CoT 기반 개선)
    
    증상 분석 결과를 바탕으로 응급도를 판단하고 다음 행동을 결정합니다.
    """
    print("\n[Node 2] 응급도 판단 중...")
    
    symptoms_analysis = state["symptoms_analysis"]
    user_query = state["user_query"]
    
    # LLM을 사용한 응급도 판단 (CoT 방식)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=800
    )
    
    # 지침 5: Chain-of-Thought (CoT) 프롬프트 - 단계적 추론 요구
    triage_prompt = f"""당신은 수의학 응급 전문의입니다. 다음 증상을 **단계적으로 분석**하여 응급도를 판단하세요.

## 사용자 질문
{user_query}

## 증상 분석 결과
{symptoms_analysis}

## 응급도 판단 프로세스 (반드시 순서대로 작성)

### 1단계: 위험 징후 확인
다음 고위험 키워드가 포함되어 있는지 확인하세요:
- 발작, 경련, 의식 저하
- 호흡곤란, 청색증, 질식
- 심한 출혈, 쇼크
- 복부 팽만 (위 비틀림 의심)
- 급성 중독, 고열 (40도 이상)

**확인 결과**: [위험 징후 유무 및 해당 키워드]

### 2단계: 증상의 급격성 평가
- 증상 발현 시간: [갑자기 / 점진적]
- 증상 진행 속도: [급속 악화 / 안정 / 개선]
- 동반 증상 수: [단일 / 복합]

**평가 결과**: [증상 급격성 설명]

### 3단계: 생명 위협도 판단
- 호흡/순환계: [정상 / 이상]
- 의식 수준: [명료 / 저하]
- 통증 강도: [경미 / 중등도 / 심각]

**판단 결과**: [생명 위협도]

### 4단계: 최종 응급도 결정
위 1-3단계 분석을 종합하여 응급도를 결정하세요:
- "높음": 생명 위협 또는 즉각적 치료 필요
- "보통": 24-48시간 내 진료 필요
- "낮음": 며칠 내 진료 가능

**최종 응급도**: [높음/보통/낮음]
**추천 진료과**: [내과/외과/안과/치과/피부과]
**근거 요약**: [1-2문장]"""
    
    response = llm.invoke([HumanMessage(content=triage_prompt)])
    triage_result = response.content
    
    # 응급도 추출 (간단한 파싱)
    if "높음" in triage_result:
        urgency = "높음"
        next_action = "recommend_hospital"
    elif "보통" in triage_result:
        urgency = "보통"
        next_action = "recommend_hospital"
    else:
        urgency = "낮음"
        next_action = "end"
    
    # 진료과 추출
    if "내과" in triage_result:
        department = "내과"
    elif "외과" in triage_result:
        department = "외과"
    elif "안과" in triage_result:
        department = "안과"
    elif "피부과" in triage_result:
        department = "피부과"
    else:
        department = "일반"
    
    # 상태 업데이트
    state["urgency_level"] = urgency
    state["recommended_department"] = department
    state["next_action"] = next_action
    state["messages"].append(AIMessage(content=f"응급도 판단:\n{triage_result}"))
    
    print(f"[Node 2 완료] 응급도: {urgency}, 진료과: {department}, 다음 액션: {next_action}")
    
    return state


def recommend_hospital_node(state: AgentState) -> AgentState:
    """
    Node 3: 병원 추천
    
    응급도와 진료과를 고려하여 적절한 병원을 추천합니다.
    """
    print("\n[Node 3] 병원 추천 중...")
    
    urgency = state["urgency_level"]
    department = state["recommended_department"]
    
    # 병원 검색 (Tool 호출)
    hospitals = hospital_recommend_tool.invoke({
        "location": "서울",  # TODO: 사용자 위치 정보 사용
        "department": department,
        "urgency": urgency
    })
    
    # 상태 업데이트
    state["hospital_list"] = hospitals
    
    # 병원 리스트 포맷팅
    hospital_text = "\n\n".join([
        f"**{h['name']}**\n"
        f"- 주소: {h['address']}\n"
        f"- 전화: {h['phone']}\n"
        f"- 24시간: {h['24hours']}\n"
        f"- 거리: {h['distance']}"
        for h in hospitals
    ])
    
    state["messages"].append(AIMessage(content=f"추천 병원:\n\n{hospital_text}"))
    state["next_action"] = "generate_final_response"
    
    print(f"[Node 3 완료] {len(hospitals)}개 병원 추천됨")
    
    return state


def generate_final_response_node(state: AgentState) -> AgentState:
    """
    Node 4: 최종 응답 생성
    
    모든 분석 결과를 종합하여 사용자에게 제공할 최종 응답을 생성합니다.
    """
    print("\n[Node 4] 최종 응답 생성 중...")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=1500
    )
    
    # 최종 응답 생성 프롬프트
    final_prompt = f"""다음 정보를 바탕으로 사용자에게 친절하고 전문적인 최종 답변을 작성하세요.

사용자 질문:
{state['user_query']}

증상 분석:
{state['symptoms_analysis']}

응급도: {state['urgency_level']}
추천 진료과: {state['recommended_department']}

추천 병원:
{state.get('hospital_list', [])}

답변 구조:
1. 증상 요약 및 공감
2. 의심 질환 설명 (전문 용어는 쉽게 풀어서)
3. 응급도 및 권장 조치
4. 추천 병원 정보 (있는 경우)
5. 추가 주의사항

따뜻하고 전문적인 톤으로 작성하세요."""
    
    response = llm.invoke([HumanMessage(content=final_prompt)])
    final_response = response.content
    
    # 상태 업데이트
    state["final_response"] = final_response
    state["messages"].append(AIMessage(content=final_response))
    state["next_action"] = "end"
    
    print(f"[Node 4 완료] 최종 응답 생성됨")
    
    return state


# ============================================================================
# Conditional Edge 함수
# ============================================================================

def should_recommend_hospital(state: AgentState) -> Literal["recommend_hospital", "generate_final_response"]:
    """
    조건부 엣지: 응급도에 따라 병원 추천 여부 결정
    
    - 응급도 '높음' 또는 '보통': 병원 추천 수행
    - 응급도 '낮음': 병원 추천 생략하고 최종 응답 생성
    """
    urgency = state.get("urgency_level", "보통")
    
    if urgency in ["높음", "보통"]:
        print(f"[조건부 엣지] 응급도 '{urgency}' → 병원 추천 수행")
        return "recommend_hospital"
    else:
        print(f"[조건부 엣지] 응급도 '{urgency}' → 병원 추천 생략")
        return "generate_final_response"


# ============================================================================
# LangGraph 워크플로우 구축
# ============================================================================

def create_pet_health_agent() -> StateGraph:
    """
    반려동물 건강 상담 Agent 워크플로우 생성
    
    Returns:
        컴파일된 StateGraph
    """
    # StateGraph 초기화
    workflow = StateGraph(AgentState)
    
    # Node 추가
    workflow.add_node("analyze_symptom", analyze_symptom_node)
    workflow.add_node("triage_and_decide", triage_and_decide_node)
    workflow.add_node("recommend_hospital", recommend_hospital_node)
    workflow.add_node("generate_final_response", generate_final_response_node)
    
    # Edge 정의
    # 시작 → 증상 분석
    workflow.set_entry_point("analyze_symptom")
    
    # 증상 분석 → 응급도 판단
    workflow.add_edge("analyze_symptom", "triage_and_decide")
    
    # 응급도 판단 → 조건부 분기 (병원 추천 or 최종 응답)
    workflow.add_conditional_edges(
        "triage_and_decide",
        should_recommend_hospital,
        {
            "recommend_hospital": "recommend_hospital",
            "generate_final_response": "generate_final_response"
        }
    )
    
    # 병원 추천 → 최종 응답
    workflow.add_edge("recommend_hospital", "generate_final_response")
    
    # 최종 응답 → 종료
    workflow.add_edge("generate_final_response", END)
    
    # 컴파일 (체크포인터 추가 가능)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    print("LangGraph 워크플로우 구축 완료")
    
    return app


# ============================================================================
# 실행 함수
# ============================================================================

def run_agent(user_query: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Agent 실행
    
    Args:
        user_query: 사용자 질문
        config: LangGraph 설정 (thread_id 등)
        
    Returns:
        최종 상태
    """
    # Agent 생성
    app = create_pet_health_agent()
    
    # 초기 상태 설정
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "symptoms_analysis": "",
        "urgency_level": "",
        "recommended_department": "",
        "hospital_list": [],
        "final_response": "",
        "next_action": ""
    }
    
    # 설정
    if config is None:
        config = {"configurable": {"thread_id": "default"}}
    
    # 실행
    print(f"\n{'='*60}")
    print(f"Agent 실행 시작: {user_query}")
    print(f"{'='*60}")
    
    final_state = None
    for state in app.stream(initial_state, config):
        # 각 단계의 상태 출력 (디버깅용)
        node_name = list(state.keys())[0]
        print(f"\n--- {node_name} 완료 ---")
        final_state = state[node_name]
    
    print(f"\n{'='*60}")
    print(f"Agent 실행 완료")
    print(f"{'='*60}\n")
    
    return final_state


# ============================================================================
# 예제 실행
# ============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    
    # 환경 변수 로드
    load_dotenv()
    
    # 테스트 쿼리
    test_queries = [
        "저희 강아지가 구토를 계속하고 황달 증상이 있어요. 호흡도 거칠어요.",
        "고양이 눈이 약간 충혈되었는데 괜찮을까요?",
        "강아지 피부에 발진이 생겼어요. 가려워하는 것 같아요."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"테스트 케이스 {i}")
        print(f"{'#'*80}")
        
        result = run_agent(query, config={"configurable": {"thread_id": f"test_{i}"}})
        
        # 최종 응답 출력
        print("\n" + "="*60)
        print("최종 응답:")
        print("="*60)
        print(result.get("final_response", "응답 생성 실패"))
        print("\n")
