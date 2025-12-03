"""
RAG와 Agent를 연동하는 고급 버전
실제 RAG 파이프라인을 Agent의 Tool로 사용
"""

import os
from typing import TypedDict, List, Dict, Any, Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 실제 RAG 컴포넌트 import
from rag_pipeline import setup_rag_pipeline, query_rag
from data_preprocessing import load_multiple_departments


# ============================================================================
# 전역 RAG 컴포넌트 (초기화 후 재사용)
# ============================================================================

RAG_COMPONENTS = None


def initialize_rag_system(data_path: str = None):
    """
    RAG 시스템 초기화 (한 번만 실행)
    """
    global RAG_COMPONENTS
    
    if RAG_COMPONENTS is not None:
        print("RAG 시스템이 이미 초기화되어 있습니다.")
        return
    
    print("RAG 시스템 초기화 중...")
    
    # 데이터 로드
    if data_path is None:
        data_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training\01.원천데이터"
    
    documents = load_multiple_departments(
        base_path=data_path,
        departments=["내과", "외과", "안과"],
        data_type="source"
    )
    
    if not documents:
        print("⚠️ 문서 로드 실패. 시뮬레이션 모드로 동작합니다.")
        RAG_COMPONENTS = None
        return
    
    # RAG 파이프라인 설정
    RAG_COMPONENTS = setup_rag_pipeline(
        documents=documents,
        use_existing_vectorstore=True,  # 기존 DB 우선 사용
        k=4
    )
    
    print("✓ RAG 시스템 초기화 완료")


# ============================================================================
# Agent State
# ============================================================================

class AgentState(TypedDict):
    messages: List[Any]
    user_query: str
    symptoms_analysis: str
    urgency_level: str
    recommended_department: str
    hospital_list: List[Dict[str, str]]
    final_response: str
    next_action: str


# ============================================================================
# Tools (실제 RAG 연동)
# ============================================================================

@tool
def rag_search_tool_real(query: str, department: str = "") -> str:
    """
    실제 RAG 검색 도구 (Vector DB 기반)
    
    Args:
        query: 검색할 증상 또는 질문
        department: 진료과 필터 (선택)
        
    Returns:
        RAG 검색 결과
    """
    global RAG_COMPONENTS
    
    if RAG_COMPONENTS is None:
        # 시뮬레이션 모드
        return f"""[시뮬레이션 모드 - RAG 시스템 미초기화]
검색어: {query}
진료과: {department}

의심 질환:
- 간 질환 (황달, 구토)
- 담도 폐쇄
- 췌장염

권장 조치: 즉시 내과 진료 필요"""
    
    try:
        # 실제 RAG 검색
        rag_chain = RAG_COMPONENTS["chain"]
        
        # department 필터가 있는 경우 검색 조건 추가
        if department:
            # Retriever에 필터 적용하여 새로운 체인 생성
            retriever = RAG_COMPONENTS["vectorstore"].as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4, "filter": {"department": department}}
            )
            
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.runnables import RunnablePassthrough
            from langchain.prompts import ChatPromptTemplate
            
            prompt = ChatPromptTemplate.from_template(
                RAG_COMPONENTS.get("prompt_template", "{context}\n\n{input}")
            )
            
            def format_docs(docs):
                return "\n\n".join([d.page_content for d in docs])
            
            filtered_chain = (
                {"context": retriever | format_docs, "input": RunnablePassthrough()}
                | prompt
                | RAG_COMPONENTS["llm"]
                | StrOutputParser()
            )
            
            result = query_rag(filtered_chain, query)
        else:
            result = query_rag(rag_chain, query)
        
        return result
    
    except Exception as e:
        return f"RAG 검색 오류: {str(e)}"


@tool
def hospital_recommend_tool_real(
    location: str = "서울",
    department: str = "내과",
    urgency: str = "높음"
) -> List[Dict[str, str]]:
    """
    실제 병원 추천 도구
    
    TODO: 카카오맵 API 연동
    """
    # 시뮬레이션 응답
    if urgency == "높음":
        return [
            {
                "name": "24시 응급 동물병원",
                "address": f"{location} 강남구 역삼동 123-45",
                "phone": "02-1234-5678",
                "24hours": "예",
                "distance": "1.2km"
            }
        ]
    else:
        return [
            {
                "name": f"{location} 동물병원",
                "address": f"{location} 논현동 456-78",
                "phone": "02-3456-7890",
                "24hours": "아니오",
                "distance": "0.8km"
            }
        ]


# ============================================================================
# Nodes (RAG 연동 버전)
# ============================================================================

def analyze_symptom_node_real(state: AgentState) -> AgentState:
    """증상 분석 - 실제 RAG 사용"""
    print("\n[Node 1] 증상 분석 (실제 RAG) 시작...")
    
    user_query = state["user_query"]
    
    # 실제 RAG 검색
    rag_result = rag_search_tool_real.invoke({
        "query": user_query,
        "department": ""
    })
    
    state["symptoms_analysis"] = rag_result
    state["messages"].append(AIMessage(content=f"증상 분석 완료:\n{rag_result}"))
    
    print(f"[Node 1 완료]")
    return state


def triage_and_decide_node_real(state: AgentState) -> AgentState:
    """응급도 판단 - LLM 기반"""
    print("\n[Node 2] 응급도 판단...")
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0.1,
        max_tokens=500
    )
    
    triage_prompt = f"""다음 증상 분석을 바탕으로 응급도를 판단하세요.

증상 분석:
{state['symptoms_analysis']}

응답 형식:
응급도: [높음/보통/낮음]
추천 진료과: [내과/외과/안과/치과/피부과]
이유: [간단한 설명]"""
    
    response = llm.invoke([HumanMessage(content=triage_prompt)])
    triage_result = response.content
    
    # 파싱
    urgency = "보통"
    if "높음" in triage_result:
        urgency = "높음"
        next_action = "recommend_hospital"
    elif "낮음" in triage_result:
        urgency = "낮음"
        next_action = "end"
    else:
        urgency = "보통"
        next_action = "recommend_hospital"
    
    # 진료과 추출
    departments = ["내과", "외과", "안과", "치과", "피부과"]
    department = next((d for d in departments if d in triage_result), "일반")
    
    state["urgency_level"] = urgency
    state["recommended_department"] = department
    state["next_action"] = next_action
    state["messages"].append(AIMessage(content=triage_result))
    
    print(f"[Node 2 완료] 응급도={urgency}, 진료과={department}")
    return state


def recommend_hospital_node_real(state: AgentState) -> AgentState:
    """병원 추천"""
    print("\n[Node 3] 병원 추천...")
    
    hospitals = hospital_recommend_tool_real.invoke({
        "location": "서울",
        "department": state["recommended_department"],
        "urgency": state["urgency_level"]
    })
    
    state["hospital_list"] = hospitals
    state["next_action"] = "generate_final_response"
    
    print(f"[Node 3 완료] {len(hospitals)}개 병원 추천")
    return state


def generate_final_response_node_real(state: AgentState) -> AgentState:
    """최종 응답 생성"""
    print("\n[Node 4] 최종 응답 생성...")
    
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0.3,
        max_tokens=1500
    )
    
    hospital_info = ""
    if state.get("hospital_list"):
        hospital_info = "\n\n추천 병원:\n" + "\n".join([
            f"- {h['name']} ({h['distance']})\n  주소: {h['address']}\n  전화: {h['phone']}"
            for h in state["hospital_list"]
        ])
    
    final_prompt = f"""사용자에게 친절하고 전문적인 최종 답변을 작성하세요.

사용자 질문: {state['user_query']}

증상 분석:
{state['symptoms_analysis']}

응급도: {state['urgency_level']}
추천 진료과: {state['recommended_department']}
{hospital_info}

따뜻하고 전문적인 톤으로 작성하세요."""
    
    response = llm.invoke([HumanMessage(content=final_prompt)])
    final_response = response.content
    
    state["final_response"] = final_response
    state["messages"].append(AIMessage(content=final_response))
    state["next_action"] = "end"
    
    print(f"[Node 4 완료]")
    return state


# ============================================================================
# Conditional Edge
# ============================================================================

def should_recommend_hospital_real(state: AgentState) -> Literal["recommend_hospital", "generate_final_response"]:
    """응급도에 따른 분기"""
    urgency = state.get("urgency_level", "보통")
    
    if urgency in ["높음", "보통"]:
        return "recommend_hospital"
    else:
        return "generate_final_response"


# ============================================================================
# Workflow 구성
# ============================================================================

def create_pet_health_agent_real() -> StateGraph:
    """실제 RAG 연동 Agent"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("analyze_symptom", analyze_symptom_node_real)
    workflow.add_node("triage_and_decide", triage_and_decide_node_real)
    workflow.add_node("recommend_hospital", recommend_hospital_node_real)
    workflow.add_node("generate_final_response", generate_final_response_node_real)
    
    workflow.set_entry_point("analyze_symptom")
    workflow.add_edge("analyze_symptom", "triage_and_decide")
    workflow.add_conditional_edges(
        "triage_and_decide",
        should_recommend_hospital_real,
        {
            "recommend_hospital": "recommend_hospital",
            "generate_final_response": "generate_final_response"
        }
    )
    workflow.add_edge("recommend_hospital", "generate_final_response")
    workflow.add_edge("generate_final_response", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def run_agent_real(user_query: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Agent 실행 (실제 RAG 연동)"""
    app = create_pet_health_agent_real()
    
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
    
    if config is None:
        config = {"configurable": {"thread_id": "default"}}
    
    print(f"\n{'='*60}")
    print(f"Agent 실행: {user_query}")
    print(f"{'='*60}")
    
    final_state = None
    for state in app.stream(initial_state, config):
        node_name = list(state.keys())[0]
        final_state = state[node_name]
    
    print(f"\n{'='*60}")
    print("Agent 실행 완료")
    print(f"{'='*60}\n")
    
    return final_state


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    load_dotenv()
    
    # RAG 시스템 초기화
    initialize_rag_system()
    
    # 테스트
    test_query = "강아지가 갑자기 구토를 여러 번 하고 배가 부풀어 올랐어요."
    
    result = run_agent_real(
        test_query,
        config={"configurable": {"thread_id": "test_real"}}
    )
    
    print("\n" + "="*60)
    print("최종 응답:")
    print("="*60)
    print(result.get("final_response", ""))
