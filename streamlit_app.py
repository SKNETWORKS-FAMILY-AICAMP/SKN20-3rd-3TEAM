"""
강아지 증상 상담 챗봇 - Streamlit UI
"""
import streamlit as st
from app.graph import graph

# 페이지 설정
st.set_page_config(
    page_title="🐕 강아지 증상 상담 챗봇",
    page_icon="🐕",
    layout="wide"
)

# 제목
st.title("🐕 강아지 증상 상담 챗봇")
st.markdown("강아지의 증상을 입력하면 AI가 분석하고 근처 동물병원을 추천해드립니다.")

# 사이드바 - 위치 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 위치 입력 필드
    location = st.text_input(
        "현재 위치",
        value="서울특별시 송파구",
        help="정확한 주소를 입력할수록 더 정확한 검색 결과를 얻을 수 있습니다.",
        placeholder="예: 서울시 송파구 방이동 12-3"
    )
    
    # 검색 반경 설정
    radius = st.select_slider(
        "검색 반경",
        options=[1000, 2000, 3000, 5000, 10000],
        value=3000,
        format_func=lambda x: f"{x/1000:.0f}km",
        help="동물병원 검색 반경을 설정합니다."
    )
    
    # 위치 입력 가이드
    with st.expander("📍 위치 입력 가이드"):
        st.markdown("""
        **정확한 검색을 위한 주소 입력 방법:**
        
        ✅ **추천 입력 예시:**
        - `서울시 송파구 방이동 12-3` (번지수 포함 - 가장 정확)
        - `서울시 송파구 방이동`
        - `서울시 송파구`
        - `경기도 성남시 분당구 정자동 123`
        
        💡 **작동 방식:**
        1. 입력한 주소를 GPS 좌표로 변환
        2. 해당 좌표 기준 반경 내 동물병원 검색
        3. 거리순으로 정렬하여 표시
        
        ⚠️ **주의:**
        - 상세한 주소일수록 정확도 향상
        - 존재하지 않는 주소는 자동으로 키워드 검색으로 전환
        """)
    
    st.markdown("---")
    st.markdown("### 📊 사용 가능한 기능")
    st.markdown("✅ 강아지 증상 상담")
    st.markdown("✅ 웹검색 자동 보완")
    st.markdown("✅ 근처 동물병원 추천")
    st.markdown(f"📍 현재 검색 반경: **{radius/1000:.0f}km**")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("강아지의 증상을 입력해주세요 (예: 강아지가 기침을 해요)"):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            try:
                # LangGraph 실행 (location과 radius 전달)
                result = graph.invoke({
                    "question": prompt,
                    "location": location,
                    "radius": radius  # 반경 추가
                })
                
                response = result.get("final_response", "응답을 생성할 수 없습니다.")
                st.markdown(response)
                
                # 응답 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 대화 초기화 버튼
if st.sidebar.button("🗑️ 대화 초기화"):
    st.session_state.messages = []
    st.rerun()
