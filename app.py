"""
Streamlit 반려동물 건강 상담 챗봇 (RAG + LangGraph Agent)
- RAG 기반 증상 분석
- LangGraph Agent 워크플로우
- 의학적 검수 (피드백 루프)
- 병원 추천 시스템
- GPS 위치 기반 병원 검색
"""

import streamlit as st
import os
import sys
from pathlib import Path
from streamlit_geolocation import streamlit_geolocation

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root / 'src'))

# ============================================================================
# RAG Core 모듈 Import (기존 파이프라인 활용)
# ============================================================================
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from agent.workflow import run_agent
    from utils.optimization import manage_persistence, get_project_path
    
    RAG_AVAILABLE = True
    print("✅ RAG 모듈 로드 완료")
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠️ RAG 모듈 로드 실패: {e}")


# ============================================================================
# Streamlit 페이지 설정
# ============================================================================
st.set_page_config(
    page_title="🐾 수의학 전문가 챗봇",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# 1. ⚙️ RAG 시스템 초기화 (캐싱)
# ============================================================================
@st.cache_resource
def initialize_rag_system():
    """
    Vector DB 로드 및 RAG 시스템 초기화
    @st.cache_resource로 앱 실행 중 단 한 번만 실행
    
    Returns:
        dict: RAG 컴포넌트 (status, retriever 등)
    """
    if not RAG_AVAILABLE:
        return {"status": "error", "message": "RAG 모듈을 불러올 수 없습니다."}
    
    try:
        # 데이터 경로 설정
        source_base_path = get_project_path(
            'data', 
            '59.반려견 성장 및 질병 관련 말뭉치 데이터',
            '3.개방데이터',
            '1.데이터',
            'Training',
            '01.원천데이터'
        )
        persist_dir = get_project_path('data', 'chroma_db')
        
        # RAG 시스템 초기화 (캐싱 시스템 활용)
        with st.spinner("🔄 RAG 시스템 초기화 중... (최초 1회만 실행됩니다)"):
            rag_result = manage_persistence(
                data_path=source_base_path,
                persist_dir=persist_dir,
                force_rebuild=False
            )
        
        return {
            "status": "success",
            "retriever": rag_result["retriever"],
            "vectorstore": rag_result["vectorstore"],
            "load_status": rag_result["status"]
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"RAG 시스템 초기화 실패: {str(e)}"
        }


# ============================================================================
# 2. 📍 초기 GPS 위치 정보 자동 요청
# ============================================================================
# 앱 로드 시 항상 실행되어 사용자에게 위치 정보 공유 여부를 묻는 모달을 띄웁니다.
initial_location = streamlit_geolocation()


# ============================================================================
# 3. 💬 세션 상태 초기화
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.location_checked = False  # 최초 위치 확인 여부

if "location_checked" not in st.session_state:
    st.session_state.location_checked = False

if "waiting_for_location" not in st.session_state:
    st.session_state.waiting_for_location = False  # 병원 추천 대기 상태

if "last_urgency" not in st.session_state:
    st.session_state.last_urgency = None  # 마지막 응급도

if "last_department" not in st.session_state:
    st.session_state.last_department = None  # 마지막 추천 진료과

if "user_gps_location" not in st.session_state:
    st.session_state.user_gps_location = None  # GPS 좌표 (lat, lon)


# ============================================================================
# 4. 🗺️ 최초 접속 시 로직 (위치 정보 기반 환영 메시지 및 추천)
# ============================================================================
if not st.session_state.location_checked:
    
    # 4-1. 위치 정보 획득 성공 시
    if initial_location and initial_location.get('latitude'):
        lat = initial_location['latitude']
        lon = initial_location['longitude']
        
        try:
            # 병원 추천 Tool 호출
            from src.utils.tools import search_nearby_hospitals
            hospital_list = search_nearby_hospitals(lat=lat, lon=lon)
            
            if hospital_list and hospital_list[0].get("error"):
                hospital_result_text = f"❌ 병원 검색 오류: {hospital_list[0]['error']}"
            elif not hospital_list:
                hospital_result_text = "주변 5km 이내에 동물병원을 찾을 수 없습니다."
            else:
                formatted_output = ["📍 사용자 위치 기준 가장 가까운 동물병원 정보입니다:\n"]
                for i, hosp in enumerate(hospital_list, 1):
                    distance_km = float(hosp['distance_m']) / 1000.0
                    formatted_output.append(
                        f"{i}. **{hosp['name']}**\n"
                        f"   - 거리: 약 {distance_km:.2f} km\n"
                        f"   - 주소: {hosp['address']}\n"
                        f"   - 전화번호: {hosp['phone']}\n"
                    )
                hospital_result_text = "\n".join(formatted_output)
            
            # 환영 메시지 및 병원 추천 결과 출력
            welcome_message = f"""안녕하세요! 🐾 **반려동물 건강 상담 챗봇**입니다.

위치 정보 공유에 감사드립니다! 📍

**현재 GPS 위치**: ({lat:.4f}, {lon:.4f})

{hospital_result_text}

---

반려동물의 증상을 자세히 알려주시면, 수의학 전문 지식을 바탕으로 분석해드리겠습니다.

**예시 질문**:
- "강아지가 구토를 계속하고 배가 부풀어 올랐어요"
- "고양이 눈이 충혈되고 눈물이 나요"
- "강아지가 기침을 하는데 괜찮을까요?"

💡 증상, 지속 시간, 반려동물의 연령 등을 자세히 알려주세요!"""
            
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        
        except Exception as e:
            # 병원 추천 실패 시 기본 환영 메시지
            welcome_message = f"""안녕하세요! 🐾 **반려동물 건강 상담 챗봇**입니다.

위치 정보를 받았으나 병원 추천 중 오류가 발생했습니다: {str(e)}

반려동물의 증상을 자세히 알려주시면, 수의학 전문 지식을 바탕으로 분석해드리겠습니다.

**예시 질문**:
- "강아지가 구토를 계속하고 배가 부풀어 올랐어요"
- "고양이 눈이 충혈되고 눈물이 나요"
- "강아지가 기침을 하는데 괜찮을까요?"

💡 증상, 지속 시간, 반려동물의 연령 등을 자세히 알려주세요!"""
            
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        
        st.session_state.location_checked = True  # 확인 완료
    
    # 4-2. 위치 정보 획득 실패/거부 또는 아직 대기 중
    elif initial_location is not None:  # None이 아니면 응답을 받았다는 의미
        welcome_message = """안녕하세요! 🐾 **반려동물 건강 상담 챗봇**입니다.

위치 정보 공유가 거부되어 일반 모드로 시작합니다.

반려동물의 증상을 자세히 알려주시면, 수의학 전문 지식을 바탕으로 분석해드리겠습니다.

**예시 질문**:
- "강아지가 구토를 계속하고 배가 부풀어 올랐어요"
- "고양이 눈이 충혈되고 눈물이 나요"
- "강아지가 기침을 하는데 괜찮을까요?"

💡 증상, 지속 시간, 반려동물의 연령 등을 자세히 알려주세요!"""
        
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        st.session_state.location_checked = True  # 확인 완료


# ============================================================================
# 5. 🎨 UI 구성
# ============================================================================

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 시스템 설정")
    
    # RAG 시스템 상태 표시
    st.subheader("📊 시스템 상태")
    
    if RAG_AVAILABLE:
        rag_components = initialize_rag_system()
        
        if rag_components["status"] == "success":
            st.success("✅ RAG 시스템 활성화")
            st.info(f"상태: {rag_components['load_status']}")
        else:
            st.error(f"❌ {rag_components['message']}")
    else:
        st.error("❌ RAG 모듈 비활성화")
    
    st.divider()
    
    # 통계 정보
    st.subheader("📈 대화 통계")
    st.metric("총 메시지 수", len(st.session_state.messages))
    
    user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    st.metric("사용자 질문 수", len(user_messages))
    
    st.divider()
    
    # 기능 설명
    st.subheader("🔍 주요 기능")
    st.markdown("""
    - ✅ **RAG 기반 증상 분석**
    - ✅ **의학적 검수 시스템**
    - ✅ **응급도 자동 판단**
    - ✅ **병원 추천 (위치 기반)**
    - ✅ **키워드 추출 최적화**
    """)
    
    st.divider()
    
    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", type="secondary"):
        st.session_state.messages = []
        st.session_state.waiting_for_location = False
        st.session_state.last_urgency = None
        st.session_state.last_department = None
        st.rerun()


# 메인 화면
st.title("🐾 반려동물 건강 상담 챗봇")
st.caption("RAG + LangGraph Agent 기반 수의학 전문 상담 시스템")

# 경고 메시지 및 GPS 위치 요청 (병원 추천 대기 중)
if st.session_state.waiting_for_location:
    st.warning("""
    🚨 **응급도가 높거나 중간으로 판단되어 병원 추천이 필요합니다!**
    
    아래 버튼을 눌러 GPS 위치를 공유하거나, 수동으로 주소를 입력해주세요.
    """)
    
    # GPS 위치 요청 버튼
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("📍 GPS 위치 공유", type="primary"):
            location_data = streamlit_geolocation()
            
            if location_data and location_data.get("latitude") and location_data.get("longitude"):
                st.session_state.user_gps_location = {
                    "lat": location_data["latitude"],
                    "lon": location_data["longitude"]
                }
                st.success(f"✅ GPS 위치 획득: ({location_data['latitude']:.4f}, {location_data['longitude']:.4f})")
            else:
                st.error("❌ GPS 위치를 가져올 수 없습니다. 브라우저 설정을 확인하거나 수동으로 주소를 입력해주세요.")
    
    with col2:
        st.caption("또는 아래 채팅창에 주소를 입력하세요 (예: '서울시 강남구 역삼동')")


# ============================================================================
# 4. 💬 채팅 인터페이스
# ============================================================================

# 기존 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 추가 정보 표시 (assistant 메시지에만)
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            
            if metadata.get("urgency_level"):
                urgency = metadata["urgency_level"]
                urgency_color = {
                    "높음": "🔴",
                    "보통": "🟡",
                    "낮음": "🟢"
                }.get(urgency, "⚪")
                
                st.info(f"""
                **판단 결과**
                - 응급도: {urgency_color} **{urgency}**
                - 추천 진료과: **{metadata.get('recommended_department', 'N/A')}**
                """)


# ============================================================================
# 5. 🏃‍♂️ 사용자 입력 처리
# ============================================================================

if user_input := st.chat_input("증상을 입력하거나 위치 정보를 알려주세요..."):
    
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # ========================================================================
    # Agent 실행
    # ========================================================================
    with st.chat_message("assistant"):
        
        # 병원 추천 대기 모드 처리
        if st.session_state.waiting_for_location:
            with st.spinner("🗺️ 주변 병원 검색 중..."):
                urgency = st.session_state.last_urgency
                department = st.session_state.last_department
                
                try:
                    from src.utils.tools import search_nearby_hospitals
                    
                    # GPS 좌표가 있으면 GPS 우선 사용, 없으면 텍스트 주소 사용
                    if st.session_state.user_gps_location:
                        gps = st.session_state.user_gps_location
                        hospital_list = search_nearby_hospitals(
                            lat=gps["lat"], 
                            lon=gps["lon"]
                        )
                        location_display = f"GPS ({gps['lat']:.4f}, {gps['lon']:.4f})"
                    else:
                        # 텍스트 주소 사용
                        location = user_input
                        hospital_list = search_nearby_hospitals(query=location)
                        location_display = location
                    
                    # 검색 결과 포맷팅
                    if hospital_list and hospital_list[0].get("error"):
                        hospital_result = f"❌ 병원 검색 오류: {hospital_list[0]['error']}"
                    elif not hospital_list:
                        hospital_result = "주변 5km 이내에 동물병원을 찾을 수 없습니다."
                    else:
                        formatted_output = ["📍 사용자 위치 기준 가장 가까운 동물병원 정보입니다:\n"]
                        for i, hosp in enumerate(hospital_list, 1):
                            distance_km = float(hosp['distance_m']) / 1000.0
                            formatted_output.append(
                                f"{i}. **{hosp['name']}**\n"
                                f"   - 거리: 약 {distance_km:.2f} km\n"
                                f"   - 주소: {hosp['address']}\n"
                                f"   - 전화번호: {hosp['phone']}\n"
                            )
                        hospital_result = "\n".join(formatted_output)
                    
                    response_text = f"""
📍 **위치 기반 병원 추천 결과**

입력하신 위치: **{location_display}**
추천 진료과: **{department}**
응급도: **{urgency}**

{hospital_result}

💡 **권장 사항**: 응급도가 {urgency}이므로 즉시 병원 방문을 권장드립니다.
"""
                except Exception as e:
                    response_text = f"""
### ⚠️ 병원 검색 오류

오류 메시지: {str(e)}

**해결 방법**:
1. GPS 위치 공유를 시도하거나, 더 구체적인 주소를 입력해주세요 (예: "서울시 강남구 역삼동")
2. KAKAO_REST_API_KEY 환경 변수를 확인해주세요.
"""
                
                st.markdown(response_text)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # 병원 추천 모드 해제
                st.session_state.waiting_for_location = False
                st.session_state.last_urgency = None
                st.session_state.last_department = None
                st.session_state.user_gps_location = None  # GPS 좌표 초기화
        
        # 일반 RAG Agent 실행
        else:
            if not RAG_AVAILABLE or rag_components["status"] != "success":
                # RAG 비활성화 시 더미 응답
                st.error("⚠️ RAG 시스템이 비활성화되어 있습니다.")
                response_text = "죄송합니다. 현재 시스템 점검 중입니다."
            else:
                # RAG Agent 실행
                with st.spinner("🔍 전문가 분석 중... (증상 분석 → 응급도 판단 → 검수)"):
                    try:
                        # LangGraph Agent 실행 (user_location 파라미터 추가)
                        result = run_agent(
                            user_query=user_input,
                            user_location=None,  # 첫 실행에서는 위치 없음, 나중에 요청
                            config={"configurable": {"thread_id": f"streamlit_{len(st.session_state.messages)}"}}
                        )
                        
                        response_text = result.get("final_response", "응답 생성에 실패했습니다.")
                        urgency_level = result.get("urgency_level", "N/A")
                        recommended_department = result.get("recommended_department", "N/A")
                        
                        # 메타데이터 저장
                        metadata = {
                            "urgency_level": urgency_level,
                            "recommended_department": recommended_department
                        }
                        
                    except Exception as e:
                        response_text = f"⚠️ 오류가 발생했습니다: {str(e)}"
                        metadata = {}
            
            # 응답 출력
            st.markdown(response_text)
            
            # 메시지 저장
            message_data = {
                "role": "assistant",
                "content": response_text
            }
            
            if 'metadata' in locals():
                message_data["metadata"] = metadata
                
                # 메타데이터 표시
                if metadata.get("urgency_level"):
                    urgency = metadata["urgency_level"]
                    urgency_color = {
                        "높음": "🔴",
                        "보통": "🟡",
                        "낮음": "🟢"
                    }.get(urgency, "⚪")
                    
                    st.info(f"""
                    **판단 결과**
                    - 응급도: {urgency_color} **{urgency}**
                    - 추천 진료과: **{metadata.get('recommended_department', 'N/A')}**
                    """)
            
            st.session_state.messages.append(message_data)
            
            # ================================================================
            # 6. 🚨 병원 추천 트리거 감지
            # ================================================================
            if "병원 추천이 필요합니다" in response_text or (
                'metadata' in locals() and 
                metadata.get("urgency_level") in ["높음", "보통"]
            ):
                st.warning("""
                🚨 **병원 추천 기능 활성화**
                
                응급도가 높거나 중간으로 판단되어 병원 방문이 권장됩니다.
                현재 위치(구/동/시)를 입력해주시면 주변 동물병원을 추천해드립니다.
                
                예시: "서울시 강남구", "부산 해운대구"
                """)
                
                # 병원 추천 대기 모드 활성화
                st.session_state.waiting_for_location = True
                
                if 'metadata' in locals():
                    st.session_state.last_urgency = metadata.get("urgency_level")
                    st.session_state.last_department = metadata.get("recommended_department")


# ============================================================================
# 7. 📌 푸터
# ============================================================================
st.divider()
st.caption("""
⚠️ **면책 조항**: 이 챗봇은 참고용 정보만 제공하며, 실제 진단은 반드시 수의사와 상담하셔야 합니다.
💡 **기술 스택**: RAG (ChromaDB) + LangGraph + OpenAI GPT-4o-mini
""")
