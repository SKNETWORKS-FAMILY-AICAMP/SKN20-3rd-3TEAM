# 🏥 의료 RAG 챗봇 - Streamlit 웹 애플리케이션 가이드

## 📋 개요

이 문서는 **Streamlit 기반 RAG(Retrieval-Augmented Generation) 웹 애플리케이션**의 설치, 구성, 실행 방법을 설명합니다.

기존의 터미널 환경에서 실행하던 RAG 시스템을 **웹 기반 인터페이스**로 변환하여, 
사용자가 쉽게 질문을 입력하고 답변을 받을 수 있도록 개선했습니다.

---

## 🎯 주요 기능

### 1. **사용자 친화적 채팅 인터페이스**
   - 💬 질문-답변 형식의 채팅 UI
   - 📱 반응형 웹 디자인
   - ✨ 실시간 스트리밍 출력

### 2. **RAG 파이프라인 통합**
   - 📄 **Retrieval**: Chroma 벡터 DB에서 Top-K=5 문서 검색
   - ⭐ **Grading**: LLM 기반 문서 관련성 평가
   - 🌐 **Web Search Fallback**: 관련 문서 부족 시 자동 웹 검색
   - 🤖 **Generation**: LLM을 통한 최종 답변 생성

### 3. **고급 기능**
   - 📚 참고 문서 출처 표시
   - 🐛 디버그 정보 확인
   - 📊 대화 통계
   - 💾 세션 상태 유지
   - 🗑️ 대화 초기화

### 4. **성능 최적화**
   - ⚡ Streamlit 캐싱을 통한 RAG 파이프라인 재사용
   - 🚀 빠른 응답 시간
   - 💪 안정적인 세션 관리

---

## 🚀 설치 및 실행

### 1단계: 환경 설정

#### (1) 필수 패키지 설치

```bash
pip install -r requirements.txt
```

**주요 패키지:**
- `streamlit>=1.28.0`: 웹 애플리케이션 프레임워크
- `langchain>=0.3.0`: LLM 오케스트레이션
- `langchain-openai>=0.2.0`: OpenAI API 통합
- `langgraph>=0.1.0`: 상태 그래프 (CRAG 패턴)
- `chromadb>=0.5.0`: 벡터 DB
- `tavily-python>=0.3.0`: 웹 검색 API

#### (2) 환경변수 설정

`.env` 파일 생성 및 API 키 설정:

```bash
# .env 파일
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx
```

**필수 API:**
- **OpenAI API**: LLM 및 Embedding 모델 (gpt-4o-mini, text-embedding-3-small)
- **Tavily API**: 웹 검색 기능 (선택사항이지만 권장)

### 2단계: 벡터 DB 준비

기존 프로젝트에서 이미 생성된 `chroma_db` 디렉토리를 사용합니다.

벡터 DB가 없다면:

```bash
python src/main.py  # 또는 기존 ingestion 스크립트 실행
```

### 3단계: Streamlit 앱 실행

```bash
streamlit run app.py
```

**기대 출력:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.xxx.xxx:8501

  For better performance, install watchdog to auto-rerun scripts
  when files change.

  $ pip install watchdog
```

자동으로 브라우저에서 `http://localhost:8501`이 열립니다.

---

## 🎨 사용 인터페이스

### 메인 화면 구성

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏥 의료 RAG 챗봇                                    [⚙️ 설정]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ 💬 대화                                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 👤 당신:                                                    │ │
│ │ 강아지 피부 질환에 대해 알려주세요.                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🤖 AI 어시스턴트:                                           │ │
│ │ 강아지 피부 질환은 다양한 원인으로 발생할 수 있습니다...   │ │
│ │ [📚 참고한 문서 (3개)]                                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ 📝 질문 입력                                                      │
│ ┌─────────────────────────────────────────────┐ ┌────────────┐ │
│ │ 질문을 입력하세요...                       │ │ 📤 제출    │ │
│ └─────────────────────────────────────────────┘ └────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

📌 사이드바 (⚙️ 설정)
├─ 🔧 시스템 상태
├─ 📋 표시 옵션
│  ├─ ☑️ 출처 정보 표시
│  └─ ☑️ 디버그 정보 표시
├─ 💬 대화 관리
│  ├─ 🗑️ 대화 초기화
│  └─ 📊 통계
├─ ❓ 도움말
└─ 💡 예시 질문
```

### 주요 UI 요소

#### 1. **채팅 영역**
   - 👤 **사용자 메시지**: 파란색 배경, 질문 내용 표시
   - 🤖 **AI 답변**: 회색 배경, 답변 내용 표시
   - 📚 **출처 정보**: 접기/펼치기 가능한 문서 목록

#### 2. **입력 영역**
   - 📝 **텍스트 상자**: 질문 입력
   - 📤 **제출 버튼**: 질문 전송

#### 3. **사이드바**
   - 🔧 **시스템 상태**: RAG 준비 여부
   - 📋 **표시 옵션**: UI 커스터마이징
   - 💬 **대화 관리**: 초기화, 통계
   - ❓ **도움말**: 사용 방법
   - 💡 **예시 질문**: 빠른 질문 선택

---

## 📊 RAG 파이프라인 상세 분석

### 처리 흐름

```
사용자 질문
    ↓
[1] RETRIEVE NODE
    └→ 벡터 DB에서 Top-K=5 문서 검색
    └→ Similarity Score 계산
    ↓
[2] GRADE DOCUMENTS NODE
    └→ LLM으로 각 문서의 관련성 평가 (Yes/No)
    └→ 관련 있는 문서만 필터링
    ↓
[3] DECISION NODE
    ├→ 관련 문서 >= 1개 → GENERATE (내부 문서 사용)
    └→ 관련 문서 == 0개 → WEB_SEARCH (웹 검색)
    ↓
[4] QUERY REWRITE NODE (필요시)
    └→ 웹 검색 쿼리 최적화
    ↓
[5] WEB SEARCH NODE (필요시)
    └→ Tavily API로 웹 검색
    └→ 결과를 내부 문서와 결합
    ↓
[6] GENERATE NODE
    └→ 최종 컨텍스트 구성
    └→ LLM으로 답변 생성
    ↓
최종 답변 + 출처 정보
```

### 핵심 파라미터

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| **Top-K** | 5 | 초기 검색 문서 수 |
| **LLM 모델** | gpt-4o-mini | OpenAI 모델 |
| **Temperature** | 0.0 | 결정론적 답변 (창의성 없음) |
| **Embedding** | text-embedding-3-small | 임베딩 모델 |
| **Web Search** | Tavily API | 웹 검색 서비스 |

---

## 🔧 세션 상태 관리

### `st.session_state` 변수

```python
st.session_state.chat_history  # 대화 기록 리스트
    └─ role: "user" 또는 "assistant"
    └─ content: 메시지 내용
    └─ timestamp: 메시지 시간
    └─ sources: 답변의 출처 정보 (assistant만)
    └─ elapsed_time: 응답 시간 (assistant만)
    └─ debug_info: 디버그 정보 (assistant만)

st.session_state.pipeline  # RAG 파이프라인 (캐시됨)
st.session_state.show_sources  # 출처 표시 여부
st.session_state.show_debug_info  # 디버그 정보 표시 여부
```

### 캐싱 전략

```python
@st.cache_resource
def initialize_rag_pipeline():
    """RAG 파이프라인은 한 번만 로드됨"""
    ...
```

- **첫 실행**: 임베딩 모델, 벡터 DB, Retriever, 파이프라인 초기화
- **이후 실행**: 캐시된 파이프라인 재사용
- **성능 향상**: 페이지 새로고침 시에도 빠른 로딩

---

## 💡 사용 예시

### 예시 1: 기본 질문

**입력:**
```
강아지 피부 질환의 증상은 무엇인가요?
```

**예상 결과:**
1. ✅ 내부 문서에서 Top-5 검색
2. ✅ LLM이 관련성 평가 → 관련 문서 선택
3. ✅ 관련 문서 존재 → 내부 문서 기반 답변 생성
4. 📚 참고 문서 3개 표시

### 예시 2: 최신 정보 질문

**입력:**
```
GPT-5의 최신 기능은 무엇인가요?
```

**예상 결과:**
1. ⚠️ 내부 문서에 GPT-5 정보 없음
2. 🌐 자동으로 웹 검색 실행
3. ✅ 웹 검색 결과 기반 답변 생성
4. 📚 참고 문서에 웹 검색 마크 표시 (🌐)

### 예시 3: 복합 질문

**입력:**
```
개의 면역 체계와 알러지 반응의 관계를 설명해주세요.
```

**예상 결과:**
1. ✅ 여러 관련 문서 검색
2. ✅ 각 문서의 관련성 평가
3. ✅ 문서들을 통합하여 종합적 답변 생성

---

## 🐛 디버그 정보 해석

### 디버그 정보 표시 활성화

사이드바 → "디버그 정보 표시" 체크

### 정보 항목

#### 1. **Similarity Scores**
```
📊 Similarity Scores:
  1. 0.8234  ← 가장 유사한 문서
  2. 0.7891
  3. 0.7234
  4. 0.6567
  5. 0.5892  ← 가장 유사도 낮은 문서
```

**해석:**
- 1.0에 가까울수록 유사도 높음
- 0.0에 가까울수록 유사도 낮음

#### 2. **관련성 판정**
```
✓ 관련성 판정:
  관련있음: 3개 (YES)
  관련없음: 2개 (NO)
```

**해석:**
- YES: LLM이 질문과 관련이 있다고 판정
- NO: LLM이 질문과 무관하다고 판정

#### 3. **웹 검색 여부**
```
🌐 웹 검색:
  ✓ 실행됨  ← 내부 문서 부족
  또는
  ✗ 미실행  ← 관련 문서 충분
```

---

## ⚙️ 고급 설정

### 1. LLM 모델 변경

`app.py`의 `initialize_rag_pipeline()` 함수:

```python
pipeline = LangGraphRAGPipeline(
    retriever,
    llm_model="gpt-4-turbo",  # ← 여기 변경
    temperature=0.0,
    debug=False
)
```

**지원 모델:**
- `gpt-4o-mini` (기본값, 빠름)
- `gpt-4-turbo` (더 정확함)
- `gpt-4o` (최신, 가장 정확함)

### 2. Top-K 값 변경

`app.py`의 `initialize_rag_pipeline()` 함수:

```python
retriever = create_retriever(
    vectorstore,
    top_k=10  # ← 기본값 5에서 변경
)
```

**권장 값:**
- Top-K=5 (기본값, 빠름)
- Top-K=10 (더 많은 문서)

### 3. 디버그 모드 활성화

`app.py`의 `initialize_rag_pipeline()` 함수:

```python
pipeline = LangGraphRAGPipeline(
    retriever,
    debug=True  # ← 터미널에 상세 로그 출력
)
```

### 4. 포트 변경

```bash
streamlit run app.py --server.port 8502
```

---

## 🚨 트러블슈팅

### 문제 1: "OPENAI_API_KEY 환경변수가 설정되지 않았습니다"

**해결방법:**
```bash
# .env 파일 생성
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# 또는 환경변수 직접 설정
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 문제 2: "Chroma DB 로드 실패"

**해결방법:**
```bash
# 벡터 DB 재구축
python src/ingestion.py
```

### 문제 3: "웹 검색이 작동하지 않음"

**해결방법:**
```bash
# Tavily API 키 설정
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx

# 또는 웹 검색 없이 실행 (내부 문서만 사용)
```

### 문제 4: "응답이 느림"

**해결방법:**
- 더 간단한 모델 사용: `gpt-4o-mini` 사용
- Top-K 값 감소: `top_k=3` 설정
- GPU 활성화 (HuggingFace Embedding 사용 시)

### 문제 5: "메모리 부족"

**해결방법:**
- Embedding 모델 변경: HuggingFace CPU 모드 사용
- 청크 크기 조정
- 배치 처리 추가

---

## 📈 성능 최적화 팁

### 1. 응답 시간 개선
- **LLM 모델**: `gpt-4o-mini` 사용 (빠른 응답)
- **Top-K 감소**: `top_k=3` 설정
- **Embedding 캐싱**: 이미 활성화됨

### 2. 답변 품질 개선
- **LLM 모델**: `gpt-4o` 사용 (더 정확함)
- **Top-K 증가**: `top_k=10` 설정
- **웹 검색 활성화**: Tavily API 설정

### 3. 메모리 효율성
- **배치 처리**: 여러 질문을 한 번에 처리
- **스트리밍 출력**: 청크 단위로 출력
- **캐싱 활용**: 이미 최적화됨

---

## 📚 파일 구조

```
third/
├── app.py                          # ← Streamlit 메인 애플리케이션
├── requirements.txt                # 필수 패키지 (streamlit 추가)
├── STREAMLIT_GUIDE.md             # ← 이 파일
├── .env                            # API 키 설정 (git 제외)
├── chroma_db/                      # 벡터 DB
├── src/
│   ├── pipeline.py                # LangGraph CRAG 파이프라인
│   ├── retrieval.py               # Retriever
│   ├── embeddings.py              # Embedding 모델
│   ├── ingestion.py               # 데이터 로딩
│   ├── chunking.py                # 문서 분할
│   └── ...
└── data/
    ├── raw/
    │   ├── disease/               # 의료 데이터
    │   └── hospital/              # 병원 정보
    └── ...
```

---

## 🔐 보안 고려사항

### 1. API 키 보호
```bash
# .env 파일은 git에서 제외됨
git check-ignore .env
```

### 2. 사용자 입력 검증
```python
# 이미 구현됨
if not question:
    st.warning("⚠️ 질문을 입력해주세요!")
    return
```

### 3. 세션 타임아웃
- Streamlit 기본 세션 타임아웃: 30분

### 4. 로깅 및 모니터링
```python
logger = get_logger(__name__)
logger.error(f"Error: {str(e)}")
```

---

## 📞 지원 및 피드백

### 문제 보고
- 터미널 에러 메시지 복사
- 디버그 정보 스크린샷
- 질문 내용 기록

### 개선 제안
- 새로운 기능 요청
- UI/UX 피드백
- 성능 최적화 아이디어

---

## 📖 참고 자료

### 공식 문서
- **Streamlit**: https://docs.streamlit.io/
- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langgraph.dev/
- **OpenAI API**: https://platform.openai.com/docs/

### 관련 프로젝트
- Chroma DB: https://www.trychroma.com/
- Tavily API: https://tavily.com/

---

**마지막 업데이트**: 2024년 12월
**버전**: 1.0.0

