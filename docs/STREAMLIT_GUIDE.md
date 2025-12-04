# 🚀 Streamlit 챗봇 실행 가이드

## 📌 개요

`app.py`는 기존 RAG/LangGraph 파이프라인을 **건드리지 않고** Streamlit으로 통합한 대화형 챗봇입니다.

---

## 🔧 설치

### 1. Streamlit 패키지 설치

```bash
pip install -r requirements_streamlit.txt
```

또는

```bash
pip install streamlit
```

### 2. 기존 패키지 확인

```bash
pip install -r requirements.txt
```

---

## 🏃 실행 방법

### 로컬 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

### 포트 변경

```bash
streamlit run app.py --server.port 8080
```

### 외부 접속 허용

```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 🎨 주요 기능

### 1. **RAG 기반 증상 분석**
- 수의학 전문 지식 베이스 검색
- 키워드 추출로 검색 정확도 향상

### 2. **LangGraph Agent 워크플로우**
```
사용자 입력
    ↓
[증상 분석] → [응급도 판단] → [의학적 검수] → [병원 추천] → [최종 응답]
```

### 3. **의학적 검수 시스템**
- 최대 2회 피드백 루프
- 생명 위협 징후 누락 방지
- 과대/과소 평가 검증

### 4. **병원 추천 시스템**
- 응급도 "높음" 또는 "보통" 시 자동 활성화
- 위치 기반 병원 추천 (카카오맵 API 연동 예정)

### 5. **캐싱 시스템**
- `@st.cache_resource`로 RAG 시스템 1회만 로드
- 2회차 실행부터 ~5초 만에 시작

---

## 📊 화면 구성

### 메인 화면
```
┌────────────────────────────────────────┐
│  🐾 반려동물 건강 상담 챗봇            │
│  RAG + LangGraph Agent 기반            │
├────────────────────────────────────────┤
│  [사용자] 강아지가 구토를 해요          │
│  [챗봇] 증상 분석 결과...              │
│  ┌──────────────────────────────────┐  │
│  │ 판단 결과                         │  │
│  │ - 응급도: 🟡 보통                │  │
│  │ - 추천 진료과: 내과               │  │
│  └──────────────────────────────────┘  │
│  ⚠️ 병원 추천 기능 활성화              │
├────────────────────────────────────────┤
│  [입력창] 증상을 입력하세요...         │
└────────────────────────────────────────┘
```

### 사이드바
```
┌──────────────────────┐
│ ⚙️ 시스템 설정       │
├──────────────────────┤
│ 📊 시스템 상태        │
│ ✅ RAG 시스템 활성화  │
│ 상태: loaded         │
├──────────────────────┤
│ 📈 대화 통계          │
│ 총 메시지 수: 10     │
│ 사용자 질문 수: 5    │
├──────────────────────┤
│ 🔍 주요 기능          │
│ - RAG 기반 증상 분석 │
│ - 의학적 검수        │
│ - 응급도 자동 판단   │
│ - 병원 추천          │
├──────────────────────┤
│ [🗑️ 대화 초기화]     │
└──────────────────────┘
```

---

## 💬 사용 예시

### 예시 1: 응급 상황 (병원 추천 활성화)

```
사용자: 강아지가 갑자기 구토를 여러 번 하고 배가 부풀어 올랐어요.

챗봇: [증상 분석]
위 확장/비틀림(GDV) 의심됩니다. 이는 매우 위험한 응급 상황으로...

[판단 결과]
- 응급도: 🔴 높음
- 추천 진료과: 내과

⚠️ 병원 추천 기능 활성화
현재 위치를 입력해주세요.

사용자: 서울시 강남구

챗봇: 📍 위치 기반 병원 추천 결과
1. 24시 응급 동물병원 (1.2km)
2. 스마일 동물 메디컬 센터 (2.5km)
```

### 예시 2: 경미한 증상

```
사용자: 고양이 눈이 약간 충혈되었는데 괜찮을까요?

챗봇: [증상 분석]
경미한 안과 증상으로 보입니다. 결막염 가능성이 있으나...

[판단 결과]
- 응급도: 🟡 보통
- 추천 진료과: 안과

1-2일 내 진료를 권장드립니다.
```

---

## 🔧 커스터마이징

### 1. 페이지 설정 변경

`app.py` 파일에서:

```python
st.set_page_config(
    page_title="🐾 수의학 전문가 챗봇",  # 변경 가능
    page_icon="🐶",                      # 변경 가능
    layout="wide",                       # "centered" 또는 "wide"
)
```

### 2. 테마 변경

`.streamlit/config.toml` 파일 생성:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### 3. 초기 메시지 변경

`app.py`에서:

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "여기에 초기 메시지 작성"  # 변경 가능
    })
```

---

## 🐛 문제 해결

### Q1: "RAG 모듈을 불러올 수 없습니다" 오류

**해결책**:
```bash
# 환경 변수 확인
cat .env

# OPENAI_API_KEY 설정 확인
echo $OPENAI_API_KEY

# 모듈 경로 확인
python -c "import sys; print(sys.path)"
```

### Q2: Vector DB 로딩이 너무 느림

**해결책**:
- 첫 실행은 ~8분 소요 (정상)
- 2회차부터 ~5초 (캐시 활용)
- `force_rebuild=True`로 설정했는지 확인

### Q3: 병원 추천이 작동하지 않음

**확인 사항**:
1. 응답에 "병원 추천이 필요합니다" 포함 여부
2. 응급도가 "높음" 또는 "보통"인지 확인
3. `st.session_state.waiting_for_location` 상태 확인

---

## 📈 성능 최적화

### 캐싱 활용

```python
@st.cache_resource  # RAG 시스템은 1회만 로드
def initialize_rag_system():
    ...

@st.cache_data  # 데이터는 TTL 설정 가능
def load_static_data():
    ...
```

### 실행 시간 측정

```python
import time

start_time = time.time()
result = run_agent(user_input)
elapsed_time = time.time() - start_time

st.metric("실행 시간", f"{elapsed_time:.2f}초")
```

---

## 🚀 배포

### Streamlit Cloud

1. GitHub에 푸시
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. 레포지토리 연결
4. `app.py` 선택
5. Deploy 클릭

### 환경 변수 설정

Streamlit Cloud에서:
```
Settings → Secrets
```

```toml
OPENAI_API_KEY = "your_key_here"
ANTHROPIC_API_KEY = "your_key_here"
```

---

## 📚 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

---

**Made with 🚀 for Pet Health AI**
