"""
Streamlit Frontend - FastAPI 클라이언트 버전
기존 streamlit_app.py를 FastAPI 백엔드 호출로 수정
"""
import os
import streamlit as st
import requests
from typing import List, Dict, Any

# FastAPI 백엔드 URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_V1 = f"{BACKEND_URL}/api/v1"

st.set_page_config(
    page_title="반려견 질병 Q&A",
    page_icon="🐶",
    layout="wide",
)


# ---------------------------
# UI 헤더
# ---------------------------
st.title("🐶 반려견 질병 상담 챗봇")
st.markdown("---")


# ---------------------------
# 사이드바 설정
# ---------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 검색 방식 선택
    search_type = st.selectbox(
        "검색 방식",
        options=["ensemble", "similarity", "bm25"],
        format_func=lambda x: {
            "ensemble": "🔀 Ensemble (Similarity + BM25)",
            "similarity": "🎯 Similarity Search",
            "bm25": "📝 BM25 Search"
        }[x]
    )
    
    # 검색 문서 개수
    k = st.slider("검색할 문서 개수", min_value=1, max_value=20, value=5)
    
    # Query Rewriting
    use_rewrite = st.checkbox("Query Rewriting 사용", value=False)
    
    st.markdown("---")
    
    # 헬스 체크
    if st.button("🏥 시스템 상태 확인"):
        try:
            response = requests.get(f"{API_V1}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                st.success("✅ 시스템 정상")
                st.json(health_data)
            else:
                st.error("❌ 시스템 오류")
        except Exception as e:
            st.error(f"❌ 백엔드 연결 실패: {str(e)}")


# ---------------------------
# 메인 채팅 영역
# ---------------------------
st.subheader("💬 질문하기")

# 사용자 입력
user_question = st.text_area(
    "강아지 증상을 입력하세요",
    height=100,
    placeholder="예: 강아지가 기침을 하고 식욕이 없어요"
)

# 질문 제출
if st.button("🔍 질문하기", type="primary"):
    if not user_question.strip():
        st.warning("질문을 입력해주세요.")
    else:
        with st.spinner("답변 생성 중..."):
            try:
                # FastAPI 백엔드 호출
                response = requests.post(
                    f"{API_V1}/chat",
                    json={
                        "question": user_question,
                        "search_type": search_type,
                        "k": k,
                        "use_rewrite": use_rewrite
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Query Rewriting 정보
                    if result.get("rewritten_query"):
                        st.info(f"🔄 재작성된 검색어: {result['rewritten_query']}")
                    
                    # AI 답변
                    st.markdown("### 🤖 AI 답변")
                    st.markdown(result["answer"])
                    
                    # 참고 문서
                    if result.get("sources"):
                        st.markdown("---")
                        st.markdown("### 📚 참고 문서")
                        
                        for i, doc in enumerate(result["sources"], 1):
                            with st.expander(f"문서 {i} - {doc.get('source_type', 'unknown')}"):
                                st.markdown(f"**내용:**\n{doc['content']}")
                                st.json(doc["metadata"])
                    
                    # 검색 정보
                    st.caption(f"검색 방식: {result['search_type']} | 문서 수: {len(result.get('sources', []))}")
                    
                else:
                    st.error(f"오류 발생: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ 요청 시간 초과. 다시 시도해주세요.")
            except requests.exceptions.ConnectionError:
                st.error("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
            except Exception as e:
                st.error(f"예상치 못한 오류: {str(e)}")


# ---------------------------
# 하단 정보
# ---------------------------
st.markdown("---")
st.markdown("""
### 📌 사용 안내
- **검색 방식**:
  - **Ensemble**: 유사도 검색 + BM25 검색 결합 (권장)
  - **Similarity**: 벡터 유사도 기반 검색
  - **BM25**: 키워드 매칭 기반 검색
  
- **Query Rewriting**: 질문을 검색에 최적화된 키워드로 변환

⚠️ **주의**: 이 챗봇은 참고용이며, 정확한 진단은 수의사 상담이 필요합니다.
""")
