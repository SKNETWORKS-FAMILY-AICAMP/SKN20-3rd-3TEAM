"""
LangGraph 그래프 정의 - 전체 대화 플로우 (웹검색 + 의도분류 + 평가 포함)
"""
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
from app.rag_chain import rag_chain
from app.maps_client import search_nearby_hospitals
from app.web_search import web_search_client
from app.config import settings


# 상태 정의
class ChatState(TypedDict):
    """대화 상태를 관리하는 TypedDict"""
    question: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    radius: Optional[int]
    intent: str
    retrieved_docs: List[Dict]
    relevance_score: float
    needs_web_search: bool
    web_search_results: List[Dict]
    rag_response: str
    quality_check: str
    feedback: str
    hospitals: List[Dict]
    hospital_text: str  # 🔧 추가: 병원 정보 텍스트
    final_response: str


def preprocess_node(state: ChatState) -> ChatState:
    """노드 A: 입력 전처리"""
    print("[노드 A] 입력 전처리 중...")
    
    question = state["question"].strip()
    
    if "location" not in state:
        state["location"] = None
    if "latitude" not in state:
        state["latitude"] = None
    if "longitude" not in state:
        state["longitude"] = None
    if "radius" not in state:
        state["radius"] = 3000
    
    state["question"] = question
    state["intent"] = "medical_consultation"
    state["needs_web_search"] = False
    state["web_search_results"] = []
    state["relevance_score"] = 0.0
    state["quality_check"] = "pass"
    state["feedback"] = ""
    state["hospital_text"] = ""  # 🔧 추가
    
    return state


def intent_classifier_node(state: ChatState) -> ChatState:
    """노드 A2: 의도 분류"""
    print("[노드 A2] 질문 의도 분류 중...")
    
    question = state["question"].lower()
    
    hospital_keywords = ["병원", "동물병원", "수의사", "어디", "위치", "찾아", "추천"]
    medical_keywords = ["증상", "아파", "기침", "설사", "구토", "절뚝", "피", "열", "무기력", "다리", "눈", "귀"]
    
    if any(keyword in question for keyword in hospital_keywords):
        if not any(keyword in question for keyword in medical_keywords):
            state["intent"] = "hospital_search"
            print("  → 의도: 병원 찾기")
            return state
    
    if any(keyword in question for keyword in medical_keywords):
        state["intent"] = "medical_consultation"
        print("  → 의도: 의료 상담")
        return state
    
    state["intent"] = "general"
    print("  → 의도: 일반 질문")
    return state


def retrieve_node(state: ChatState) -> ChatState:
    """노드 B: RAG 검색"""
    print("[노드 B] 관련 문서 검색 중...")
    
    question = state["question"]
    documents = rag_chain.retrieve(question)
    
    state["retrieved_docs"] = [
        {
            "content": doc.page_content,
            "disease": doc.metadata.get("disease", "Unknown"),
            "symptom": doc.metadata.get("symptom", "Unknown")
        }
        for doc in documents
    ]
    
    if documents:
        first_doc = documents[0].page_content.lower()
        question_lower = question.lower()
        keywords = ["증상", "질병", "강아지", "개", "수의", "병원", "치료"]
        matches = sum(1 for kw in keywords if kw in first_doc and kw in question_lower)
        state["relevance_score"] = min(matches / len(keywords), 1.0)
    else:
        state["relevance_score"] = 0.0
    
    print(f"  → {len(state['retrieved_docs'])}개 문서 검색 완료 (관련도: {state['relevance_score']:.2f})")
    
    if state["relevance_score"] < 0.3:
        print("  → 관련도가 매우 낮습니다. 일반 조언이 제공될 수 있습니다.")
    
    if state["relevance_score"] < settings.RELEVANCE_THRESHOLD and settings.WEB_SEARCH_ENABLED:
        state["needs_web_search"] = True
        print("  → 관련도가 낮아 웹검색이 필요합니다.")
    
    return state


def web_search_node(state: ChatState) -> ChatState:
    """노드 C: 웹검색 (조건부)"""
    if not state.get("needs_web_search", False):
        print("[노드 C] 웹검색 건너뜀 (RAG 결과 충분)")
        return state
    
    print("[노드 C] 웹검색 실행 중...")
    
    question = state["question"]
    
    try:
        search_results = web_search_client.search_korean(question, max_results=3)
        state["web_search_results"] = search_results
        print(f"  → {len(search_results)}개 웹검색 결과 발견")
    except Exception as e:
        print(f"  → 웹검색 실패 또는 타임아웃: {e}")
        state["web_search_results"] = []
    
    return state


def generate_response_node(state: ChatState) -> ChatState:
    """노드 D: LLM 응답 생성"""
    print("[노드 D] LLM 답변 생성 중...")
    
    question = state["question"]
    
    from langchain.schema import Document
    documents = [
        Document(
            page_content=doc["content"],
            metadata={"disease": doc["disease"], "symptom": doc["symptom"]}
        )
        for doc in state["retrieved_docs"]
    ]
    
    if state.get("web_search_results"):
        for web_result in state["web_search_results"]:
            web_doc = Document(
                page_content=f"[웹검색 결과]\n제목: {web_result['title']}\n내용: {web_result['content']}",
                metadata={"source": "web_search", "url": web_result.get('url', '')}
            )
            documents.append(web_doc)
        print("  → 웹검색 결과를 컨텍스트에 추가했습니다.")
    
    try:
        response = rag_chain.generate_response(question, documents)
        state["rag_response"] = response
        print("  → 답변 생성 완료")
    except Exception as e:
        print(f"  → LLM 응답 생성 실패: {e}")
        
        fallback_response = f"""
[데이터베이스에 정확히 일치하는 정보가 없습니다]

질문하신 증상 "{question}"에 대해 데이터베이스에서 정확한 정보를 찾지 못했습니다.

하지만 일반적으로 강아지의 비정상적인 행동은 다음과 같은 원인이 있을 수 있습니다:

**1. 흥분 또는 놀이 행동**
- 강아지가 기분이 좋거나 흥분했을 때 평소와 다른 행동을 보일 수 있습니다.

**2. 주의를 끌기 위한 행동**
- 보호자의 관심을 받고 싶을 때 특이한 행동을 할 수 있습니다.

**3. 신체적 불편함**
- 특정 부위에 불편함이나 가벼운 통증이 있을 때 이상 행동을 보일 수 있습니다.

⚠️ **다음과 같은 경우 즉시 동물병원을 방문하세요:**
- 행동이 계속 반복되거나 빈도가 증가하는 경우
- 다른 증상(구토, 설사, 식욕 저하, 무기력)이 동반되는 경우
- 평소와 확연히 다른 비정상적인 행동이 지속되는 경우

💡 **권장사항:**
아래 추천 동물병원에 문의하여 수의사의 정확한 진단을 받으시기를 권장합니다.
"""
        state["rag_response"] = fallback_response.strip()
        print(f"  → 일반 조언으로 대체했습니다.")
    
    return state


def quality_check_node(state: ChatState) -> ChatState:
    """노드 E: 답변 품질 평가"""
    print("[노드 E] 답변 품질 평가 중...")
    
    rag_response = state.get("rag_response", "")
    question = state["question"]
    
    if len(rag_response) < 50:
        state["quality_check"] = "fail"
        state["feedback"] = "답변이 너무 짧습니다."
        print("  → 평가: FAIL (답변 너무 짧음)")
        return state
    
    question_keywords = question.lower().split()
    response_lower = rag_response.lower()
    
    keyword_match = sum(1 for kw in question_keywords if kw in response_lower)
    
    if keyword_match < 2:
        state["quality_check"] = "fail"
        state["feedback"] = "질문과 관련성이 낮습니다."
        print("  → 평가: FAIL (관련성 낮음)")
        return state
    
    if state.get("intent") == "medical_consultation":
        if "병원" not in response_lower:
            state["quality_check"] = "fail"
            state["feedback"] = "병원 방문 권고가 없습니다."
            print("  → 평가: FAIL (병원 권고 없음)")
            return state
    
    state["quality_check"] = "pass"
    print("  → 평가: PASS ✅")
    return state


def rewrite_node(state: ChatState) -> ChatState:
    """노드 F: 답변 재생성"""
    print("[노드 F] 피드백 기반 답변 재생성 중...")
    
    question = state["question"]
    previous_response = state.get("rag_response", "")
    feedback = state.get("feedback", "")
    
    rewrite_prompt = f"""
이전 답변이 다음 이유로 부족했습니다:
{feedback}

질문: {question}

이전 답변:
{previous_response}

위 피드백을 반영하여 더 나은 답변을 작성해주세요.
특히 다음 사항을 포함해주세요:
1. 질문과 관련된 증상 설명
2. 주의사항
3. 병원 방문 권고
"""
    
    from langchain.schema import Document
    documents = [Document(page_content=rewrite_prompt, metadata={})]
    
    try:
        response = rag_chain.generate_response(question, documents)
        state["rag_response"] = response
        state["quality_check"] = "pass"
        print("  → 재생성 완료")
    except Exception as e:
        print(f"  → 재생성 실패: {e}")
    
    return state


def search_hospitals_node(state: ChatState) -> ChatState:
    """노드 G: 동물병원 검색"""
    print("[노드 G] 동물병원 검색 중...")
    
    location = state.get("location")
    radius = state.get("radius", 3000)
    
    if not location:
        print("  → 위치 정보 없음, 서울 기준으로 검색")
        location = "서울특별시"
    
    try:
        # 🔧 search_nearby_hospitals 함수 직접 호출
        hospital_text = search_nearby_hospitals(
            location=location,
            radius=radius
        )
        
        # 🔧 텍스트를 별도 필드에 저장
        state["hospital_text"] = hospital_text
        state["hospitals"] = []  # API용 빈 리스트
        
        print(f"  → 병원 검색 완료")
    except Exception as e:
        print(f"  → 병원 검색 실패: {e}")
        state["hospital_text"] = ""
        state["hospitals"] = []
    
    return state


def finalize_response_node(state: ChatState) -> ChatState:
    """노드 H: 최종 응답 통합"""
    print("[노드 H] 최종 응답 통합 중...")
    
    rag_response = state["rag_response"]
    hospital_text = state.get("hospital_text", "")  # 🔧 변경
    web_results = state.get("web_search_results", [])
    used_web_search = state.get("needs_web_search", False) and len(web_results) > 0
    
    final_parts = []
    
    final_parts.append("=" * 50)
    if used_web_search:
        final_parts.append("📊 **정보 출처: VectorDB + 웹검색** 🌐")
        final_parts.append("(VectorDB에 충분한 정보가 없어 웹에서 추가 검색했습니다)")
    else:
        final_parts.append("📊 **정보 출처: VectorDB** 📚")
        final_parts.append("(업로드된 강아지 증상 데이터베이스에서 정보를 가져왔습니다)")
    final_parts.append("=" * 50 + "\n")
    
    final_parts.append(rag_response)
    
    if web_results:
        final_parts.append("\n\n" + "=" * 50)
        final_parts.append("\n🔍 **웹검색으로 추가 확인한 자료**\n")
        for i, result in enumerate(web_results[:3], 1):
            if result.get('url'):
                final_parts.append(f"\n{i}. **{result['title']}**")
                final_parts.append(f"   🔗 출처: {result['url']}")
                content_preview = result.get('content', '')[:150]
                if content_preview:
                    final_parts.append(f"   💬 요약: {content_preview}...")
            else:
                final_parts.append(f"\n{i}. **{result['title']}** (AI 요약)")
    
    # 🔧 병원 정보 출력 수정
    if hospital_text:
        final_parts.append("\n\n" + "=" * 50)
        final_parts.append(hospital_text)
    else:
        final_parts.append("\n\n⚠️ 근처 동물병원 정보를 찾지 못했습니다.")
    
    state["final_response"] = "\n".join(final_parts)
    print("  → 최종 응답 완성")
    
    return state


def route_after_intent(state: ChatState) -> str:
    """의도에 따라 다음 노드 결정"""
    intent = state.get("intent", "medical_consultation")
    
    if intent == "hospital_search":
        return "search_hospitals"
    else:
        return "retrieve"


def route_after_quality_check(state: ChatState) -> str:
    """평가 결과에 따라 다음 노드 결정"""
    quality_check = state.get("quality_check", "pass")
    
    if quality_check == "fail":
        return "rewrite"
    else:
        return "search_hospitals"


def create_graph() -> StateGraph:
    """LangGraph 그래프 생성"""
    
    workflow = StateGraph(ChatState)
    
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_response_node)
    workflow.add_node("quality_evaluator", quality_check_node)
    workflow.add_node("rewrite", rewrite_node)
    workflow.add_node("search_hospitals", search_hospitals_node)
    workflow.add_node("finalize", finalize_response_node)
    
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "intent_classifier")
    
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "retrieve": "retrieve",
            "search_hospitals": "search_hospitals"
        }
    )
    
    workflow.add_edge("retrieve", "web_search")
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", "quality_evaluator")
    
    workflow.add_conditional_edges(
        "quality_evaluator",
        route_after_quality_check,
        {
            "rewrite": "rewrite",
            "search_hospitals": "search_hospitals"
        }
    )
    
    workflow.add_edge("rewrite", "search_hospitals")
    workflow.add_edge("search_hospitals", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


graph = create_graph()