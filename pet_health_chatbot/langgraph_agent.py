"""
LangGraph Agent 워크플로우 구현
증상 분석 → 응급도 판단 → 병원 추천 자동화 워크플로우
"""

import os
from typing import TypedDict, Annotated, Literal, Dict, Any, List
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver


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
# Tool 정의
# ============================================================================

@tool
def rag_search_tool(query: str, department: str = "") -> str:
    """
    RAG 검색 도구: 수의학 지식 베이스에서 관련 정보 검색
    
    Args:
        query: 검색할 증상 또는 질문
        department: 진료과 필터 (선택 사항)
        
    Returns:
        검색된 관련 정보
    """
    # 실제 구현에서는 RAG 파이프라인을 호출
    # 여기서는 시뮬레이션
    
    print(f"[RAG Search] Query: {query}, Department: {department}")
    
    # TODO: 실제 RAG 파이프라인 연동
    # from rag_pipeline import query_rag
    # result = query_rag(rag_chain, query)
    
    # 시뮬레이션 응답
    simulated_response = f"""
    [검색 결과 - {department}과]
    
    증상: {query}
    
    의심 질환:
    - 간 질환 (황달, 구토 동반)
    - 담도 폐쇄
    - 췌장염
    
    주의사항:
    - 황달은 심각한 징후일 수 있습니다.
    - 즉시 수의사 진료가 필요합니다.
    
    권장 조치:
    - 24시간 이내 내과 진료 권장
    - 혈액 검사 및 초음파 검사 필요
    """
    
    return simulated_response


@tool
def hospital_recommend_tool(
    location: str = "서울",
    department: str = "내과",
    urgency: str = "높음"
) -> List[Dict[str, str]]:
    """
    병원 추천 도구: 지역 및 진료과 기반 동물병원 추천
    
    Args:
        location: 위치 (시/도 또는 구/동)
        department: 진료과
        urgency: 응급도 ("높음", "보통", "낮음")
        
    Returns:
        추천 병원 리스트 (이름, 주소, 전화번호, 24시간 운영 여부)
    """
    print(f"[Hospital Recommend] Location: {location}, Dept: {department}, Urgency: {urgency}")
    
    # TODO: 실제 지도 API (카카오맵, 네이버 지도) 연동
    # 실제 구현에서는 kakao_map_server.py의 API를 호출
    
    # 시뮬레이션 응답
    if urgency == "높음":
        hospitals = [
            {
                "name": "24시 응급 동물병원",
                "address": "서울 강남구 역삼동 123-45",
                "phone": "02-1234-5678",
                "24hours": "예",
                "distance": "1.2km"
            },
            {
                "name": "스마일 동물 메디컬 센터",
                "address": "서울 강남구 삼성동 678-90",
                "phone": "02-2345-6789",
                "24hours": "예",
                "distance": "2.5km"
            }
        ]
    else:
        hospitals = [
            {
                "name": "우리 동물병원",
                "address": "서울 강남구 논현동 456-78",
                "phone": "02-3456-7890",
                "24hours": "아니오",
                "distance": "0.8km"
            }
        ]
    
    return hospitals


# ============================================================================
# Node 함수 정의
# ============================================================================

def analyze_symptom_node(state: AgentState) -> AgentState:
    """
    Node 1: 증상 분석 (RAG 검색 수행)
    
    사용자의 질문을 분석하고 RAG를 통해 관련 정보를 검색합니다.
    """
    print("\n[Node 1] 증상 분석 시작...")
    
    user_query = state["user_query"]
    
    # RAG 검색 수행 (Tool 호출 시뮬레이션)
    # 실제로는 LLM이 Tool을 사용하도록 설정
    rag_result = rag_search_tool.invoke({"query": user_query, "department": ""})
    
    # 상태 업데이트
    state["symptoms_analysis"] = rag_result
    state["messages"].append(AIMessage(content=f"증상 분석 완료:\n{rag_result}"))
    
    print(f"[Node 1 완료] 분석 결과 저장됨")
    
    return state


def triage_and_decide_node(state: AgentState) -> AgentState:
    """
    Node 2: 응급도 판단 및 다음 단계 결정
    
    증상 분석 결과를 바탕으로 응급도를 판단하고 다음 행동을 결정합니다.
    """
    print("\n[Node 2] 응급도 판단 중...")
    
    symptoms_analysis = state["symptoms_analysis"]
    
    # LLM을 사용한 응급도 판단
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=500
    )
    
    triage_prompt = f"""다음 증상 분석 결과를 바탕으로 응급도를 판단하세요.

증상 분석:
{symptoms_analysis}

응급도를 다음 중 하나로 분류하세요:
- "높음": 생명을 위협하거나 즉각적인 치료가 필요한 경우
- "보통": 24-48시간 내 진료가 필요한 경우
- "낮음": 며칠 내 진료하면 되는 경우

또한 추천 진료과를 명시하세요 (내과, 외과, 안과, 치과, 피부과 중 선택).

응답 형식:
응급도: [높음/보통/낮음]
추천 진료과: [진료과명]
이유: [1-2문장 설명]"""
    
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
