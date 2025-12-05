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
    question: str                    # 사용자 질문
    location: Optional[str]          # 위치 정보 (예: "서울 강남구")
    latitude: Optional[float]        # 위도 좌표
    longitude: Optional[float]       # 경도 좌표
    radius: Optional[int]           # 동물병원 검색 반경 (미터)
    intent: str                     # 질문 의도 (medical_consultation/hospital_search/general)
    retrieved_docs: List[Dict]      # RAG 검색 문서 리스트
    relevance_score: float          # 질문과 각 문서의 관련도 점수 (0-1)
    needs_web_search: bool          # 웹검색 필요 여부
    web_search_results: List[Dict]  # Tavily 웹검색 결과
    rag_response: str               # LLM이 생성한 RAG 기반 응답
    quality_check: str              # 응답 품질 평가 결과 (pass/fail)
    feedback: str                   # 품질 평가 피드백 메시지
    hospitals: List[Dict]           # 근처 동물병원 정보 리스트 (API용)
    hospital_text: str              # 병원 정보 텍스트 (출력용)
    final_response: str             # 최종 통합 응답 (RAG + 웹검색 + 병원정보)


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
    """노드 A2: 의도 분류
    현재는 키워드 기반 분류 방식임
    (특정 키워드가 들어가면 특정 노드로 분류)

    이걸 
    1차- 키워드로 빠른 분류, 2차-llm이 분류해주는 방식으로 수정 (-> 고도화 작업에서 ㄱㄱ)
    
    
    """
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
    
    # 문서 관련성 평가 노드로 이동
    return grade_documents_node(state)


def grade_documents_node(state: ChatState) -> ChatState:
    """
    문서관련성 평가 노드
    => 검색된 문서의 관련성 여부를 llm 평가 / 관련없으면 웹 검색 플래그를 활성
    """
    print("[문서 관련성 평가] 시작...")
    
    question = state["question"]
    retrieved_docs = state["retrieved_docs"]
    filtered_docs = []
    grade_results = []
    
    if not retrieved_docs:
        state["needs_web_search"] = True
        print("  → 검색된 문서 없음 → 웹 검색 필요!")
        return state
    
    # LLM을 사용한 관련도 평가
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage
    
    try:
        llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0)
        
        for i, doc_dict in enumerate(retrieved_docs, 1):
            doc_content = doc_dict["content"][:500]  # 길이 제한
            
            relevance_prompt = f"""
다음 질문과 검색된 문서가 서로 관련이 있는지 판단해주세요.

질문: "{question}"

검색된 문서:
"{doc_content}"

질문이 강아지 증상에 관한 것이고, 문서가 해당 증상이나 질병에 대한 정보를 담고 있다면 관련이 있습니다.

"yes" 또는 "no"로만 답변하세요.
"""
            
            response = llm.invoke([HumanMessage(content=relevance_prompt)])
            result_text = response.content.strip().lower()
            
            if "yes" in result_text:
                filtered_docs.append(doc_dict)
                grade_results.append("relevant")
                print(f"  → 문서 {i}: 관련있음")
            elif "no" in result_text:
                grade_results.append("not_relevant")
                print(f"  → 문서 {i}: 관련없음")
            else:
                # 예상치 못한 응답시 키워드 방식으로 fallback
                doc_lower = doc_content.lower()
                question_lower = question.lower()
                keywords = ["증상", "질병", "강아지", "개", "수의", "병원", "치료"]
                matches = sum(1 for kw in keywords if kw in doc_lower and kw in question_lower)
                
                if matches >= 2:
                    filtered_docs.append(doc_dict)
                    grade_results.append("relevant")
                    print(f"  → 문서 {i}: LLM 응답 실패, 키워드로 관련있음 판정")
                else:
                    grade_results.append("not_relevant")
                    print(f"  → 문서 {i}: LLM 응답 실패, 키워드로 관련없음 판정")

                    
    except Exception as e:
        print(f"  → LLM 관련도 평가 실패: {e}, 키워드 방식으로 대체")
        # LLM 호출 실패시 기존 키워드 방식으로 fallback
        for i, doc_dict in enumerate(retrieved_docs, 1):
            doc_lower = doc_dict["content"].lower()
            question_lower = question.lower()
            keywords = ["증상", "질병", "강아지", "개", "수의", "병원", "치료"]
            matches = sum(1 for kw in keywords if kw in doc_lower and kw in question_lower)
            
            if matches >= 2:
                filtered_docs.append(doc_dict)
                grade_results.append("relevant")
            else:
                grade_results.append("not_relevant")
    

    # 관련 문서가 3개 미만이면 웹 검색 필요
    if len(filtered_docs) < 3:
        state["needs_web_search"] = True
        print(f"  → 관련 문서 {len(filtered_docs)}개 (3개 미만) → 웹 검색 필요!")
    else:
        state["needs_web_search"] = False
        print(f"  → {len(filtered_docs)}개 관련 문서 확보! (3개 이상)")
    
    # 필터링된 문서로 업데이트
    state["retrieved_docs"] = filtered_docs
    
    return state


def web_search_node(state: ChatState) -> ChatState:
    # """노드 C: 웹검색 (조건부)"""
    # if not state.get("needs_web_search", False):
    #     print("[노드 C] 웹검색 건너뜀 (RAG 결과 충분)")
    #     return state
    
    # print("[노드 C] 웹검색 실행 중...")
    
    # question = state["question"]
    
    # try:
    #     search_results = web_search_client.search_korean(question, max_results=3)
    #     state["web_search_results"] = search_results
    #     print(f"  → {len(search_results)}개 웹검색 결과 발견")
    # except Exception as e:
    #     print(f"  → 웹검색 실패 또는 타임아웃: {e}")
    #     state["web_search_results"] = []
    
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
    print("  → 평가: PASS")
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


def hospital_search_node(state: ChatState) -> ChatState:
    """노드: 병원 검색 전용 노드 (의도가 hospital_search일 때)"""
    print("[병원 검색 노드] 카카오맵 API로 동물병원 검색 중...")
    
    question = state["question"]
    location = state.get("location", "서울특별시")
    radius = state.get("radius", 3000)
    
    try:
        # 카카오맵 API를 사용한 병원 검색
        hospital_text = search_nearby_hospitals(
            location=location,
            radius=radius
        )
        
        # 검색 결과를 최종 응답으로 설정
        state["final_response"] = f"""
🏥 **동물병원 검색 결과**

질문: {question}
검색 지역: {location}
검색 반경: {radius}m

{hospital_text}

💡 **이용 팁:**
- 방문 전 미리 전화로 진료 시간을 확인하세요
- 응급 상황이라면 24시간 응급동물병원을 이용하세요
- 반려견의 증상을 자세히 메모해가시면 진료에 도움됩니다
"""
        
        state["hospital_text"] = hospital_text
        state["hospitals"] = []
        
        print("  → 병원 검색 및 응답 생성 완료")
        
    except Exception as e:
        print(f"  → 병원 검색 실패: {e}")
        state["final_response"] = f"""
⚠️ **병원 검색 중 오류가 발생했습니다**

질문: {question}

죄송합니다. 현재 동물병원 검색 서비스에 일시적인 문제가 있습니다.

**대안:**
1. 네이버/구글 지도에서 "동물병원 + 지역명"으로 직접 검색
2. 동물병원 예약 앱 (펫닥터, 24시펫병원 등) 이용
3. 지역 동물병원 전화번호부 확인

응급상황이라면 119에 문의하여 가까운 응급동물병원을 안내받으세요.
"""
        state["hospital_text"] = ""
        state["hospitals"] = []
    
    return state


def search_hospitals_node(state: ChatState) -> ChatState:
    """노드 G: 동물병원 검색 (의료상담 후 병원 추천용)"""
    print("[노드 G] 동물병원 검색 중...")
    
    location = state.get("location")
    radius = state.get("radius", 3000)
    
    if not location:
        print("  → 위치 정보 없음, 서울 기준으로 검색")
        location = "서울특별시"
    
    try:
        # 카카오맵 API를 사용한 병원 검색
        hospital_text = search_nearby_hospitals(
            location=location,
            radius=radius
        )
        
        state["hospital_text"] = hospital_text
        state["hospitals"] = []
        
        print(f"  → 병원 검색 완료")
    except Exception as e:
        print(f"  → 병원 검색 실패: {e}")
        state["hospital_text"] = ""
        state["hospitals"] = []
    
    return state


def general_response_node(state: ChatState) -> ChatState:
    """노드: 일반 질문 처리 (의도가 general일 때)"""
    print("[일반 질문 노드] 일반 대화 처리 중...")
    
    question = state["question"]
    
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema.output_parser import StrOutputParser
    
    try:
        llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
당신은 친절한 한국어 AI 어시스턴트입니다.

사용자의 일반적인 질문에 도움이 되는 답변을 제공하세요.
만약 강아지 관련 질문이라면, 간단한 일반 정보는 제공하되 구체적인 의료 상담이 필요한 경우 "강아지 증상에 대해 더 자세히 문의하시려면 의료 상담 기능을 이용해주세요"라고 안내하세요.

답변은 친근하고 도움이 되도록 작성해주세요.
"""),
            ("human", "{question}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"question": question})
        
        state["final_response"] = f"""
💬 **일반 질문 답변**

{response}

---
💡 **도움말:**
- 강아지 증상 상담: "강아지가 [증상] 해요" 형태로 질문해주세요
- 동물병원 찾기: "[지역] 동물병원 찾아주세요" 형태로 질문해주세요
"""
        
        print("  → 일반 질문 답변 생성 완료")
        
    except Exception as e:
        print(f"  → 일반 질문 처리 실패: {e}")
        state["final_response"] = f"""
💬 **답변**

안녕하세요! 질문해주셔서 감사합니다.

현재 일시적인 문제로 상세한 답변을 드리기 어렵습니다.

**이용 가능한 기능:**
- 강아지 증상 상담: "강아지가 [증상명]을 해요" 형태로 질문
- 동물병원 찾기: "[지역명] 동물병원 찾아주세요" 형태로 질문

다시 질문해주시면 더 나은 서비스를 제공해드리겠습니다.
"""
    
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
    """의도에 따라 다음 노드 결정 (3갈래)"""
    intent = state.get("intent", "medical_consultation")
    
    if intent == "hospital_search":
        print(f"  → 라우팅: {intent} → hospital_search_node")
        return "hospital_search"
    elif intent == "medical_consultation":
        print(f"  → 라우팅: {intent} → retrieve_node")
        return "retrieve"
    else:  # general
        print(f"  → 라우팅: {intent} → general_response")
        return "general_response"


def route_after_quality_check(state: ChatState) -> str:
    """평가 결과에 따라 다음 노드 결정"""
    quality_check = state.get("quality_check", "pass")
    
    if quality_check == "fail":
        return "rewrite"
    else:
        return "search_hospitals"


def create_graph() -> StateGraph:
    """LangGraph 그래프 생성 - 3갈래 플로우"""
    
    workflow = StateGraph(ChatState)
    
    # 노드 추가
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    
    # 3갈래 분기용 노드들
    workflow.add_node("retrieve", retrieve_node)  # 의료상담용 RAG 검색
    workflow.add_node("hospital_search", hospital_search_node)  # 병원검색 전용
    workflow.add_node("general_response", general_response_node)  # 일반질문 처리
    
    # 의료상담 플로우 노드들
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_response_node) 
    workflow.add_node("quality_evaluator", quality_check_node)
    workflow.add_node("rewrite", rewrite_node)  # 재생성 노드
    workflow.add_node("search_hospitals", search_hospitals_node)  # 의료상담 후 병원검색
    workflow.add_node("finalize", finalize_response_node)
    
    # 시작점과 의도 분류
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "intent_classifier")
    
    # 의도별 3갈래 분기
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "retrieve": "retrieve",  # 의료상담 → RAG 검색
            "hospital_search": "hospital_search",  # 병원검색 → 병원검색 노드
            "general_response": "general_response"  # 일반질문 → 일반응답 노드
        }
    )
    
    # 의료상담 플로우 (retrieve → grade_documents → web_search/generate)
    workflow.add_edge("retrieve", "web_search")  # grade_documents_node는 retrieve_node 안에서 처리
    
    # 웹검색 후 답변 생성
    workflow.add_edge("web_search", "generate")
    
    # 답변 품질 평가 후 재생성 여부 결정
    workflow.add_edge("generate", "quality_evaluator")
    
    workflow.add_conditional_edges(
        "quality_evaluator",
        route_after_quality_check,
        {
            "rewrite": "rewrite",  # 품질 낮음 → 재생성
            "search_hospitals": "search_hospitals"  # 품질 OK → 병원검색
        }
    )
    
    # 재생성 후 병원검색으로 이동
    workflow.add_edge("rewrite", "search_hospitals")
    
    # 의료상담의 병원검색 후 최종 응답 통합
    workflow.add_edge("search_hospitals", "finalize")
    
    # 종료점들
    workflow.add_edge("hospital_search", END)  # 병원검색은 바로 종료
    workflow.add_edge("general_response", END)  # 일반질문도 바로 종료
    workflow.add_edge("finalize", END)  # 의료상담은 finalize 후 종료
    
    return workflow.compile()


graph = create_graph()