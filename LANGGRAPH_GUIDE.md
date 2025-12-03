# 🐾 LangGraph 기반 반려동물 의료 RAG 어시스턴트

## 📌 개요

이 프로젝트는 **CRAG(Corrective RAG)** 패턴을 **LangGraph**로 구현한 반려동물 의료 어시스턴트입니다.

### 🎯 핵심 특징

```
질문 분류 → 문서 검색 → 관련성 평가 → 조건부 웹 검색 → 답변 생성
  (Classify)  (Retrieve)  (Grade)      (Web Search)    (Generate)
                                              ↑
                                          필요시만 수행
```

---

## 🚀 빠른 시작

### 1️⃣ 설치

```bash
# LangGraph 의존성 설치
pip install -r requirements_langgraph.txt
```

### 2️⃣ 환경 변수 설정

`.env` 파일 생성:

```env
OPENAI_API_KEY=sk-...your_key...
TAVILY_API_KEY=...your_tavily_key...
```

#### API 키 획득

**OpenAI API 키:**
- https://platform.openai.com/api-keys
- GPT-4o-mini 모델 사용

**Tavily API 키:**
- https://app.tavily.com
- 웹 검색 서비스

### 3️⃣ 실행

```bash
# CLI 모드 (대화형)
python pet_medical_cli.py

# 또는 직접 실행
python pet_medical_rag_langgraph.py
```

---

## 📊 워크플로우 구조

### StateGraph 다이어그램

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌──────────────────┐
│  CLASSIFY 노드   │
│  질문 분류       │
│ (의료/병원/일반)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  RETRIEVE 노드   │
│  벡터 검색       │
│ (의료만 검색)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GRADE 노드      │
│  관련성 평가     │
└────┬─────────┬───┘
     │         │
  YES│         │NO
     │         │
     ▼         ▼
 GENERATE  WEB_SEARCH
     │         │
     │         ▼
     │    Tavily 검색
     │         │
     └────┬────┘
          │
          ▼
     ┌─────────────┐
     │  GENERATE   │
     │  답변 생성   │
     └──────┬──────┘
            │
            ▼
         ┌─────┐
         │ END │
         └─────┘
```

---

## 🔧 각 노드 설명

### 1. CLASSIFY 노드 (질문 분류)

**역할:** 사용자 질문을 분류

```
입력: "강아지가 구토를 해요"
처리: GPT-4o-mini로 분류
출력: classification = "medical"
```

**분류 종류:**
- `medical` - 의료 관련 (증상, 치료, 예방 등)
- `hospital` - 병원 관련 (위치, 진료시간 등)
- `general` - 일반 정보 (훈련, 여행, 기본 관리)

### 2. RETRIEVE 노드 (문서 검색)

**역할:** 벡터 저장소에서 관련 문서 검색

```
입력: question, classification
처리:
  - classification == 'medical'이면 벡터 검색
  - 아니면 스킵
출력: documents (상위 3개)
```

**벡터 저장소:**
- Chroma 사용
- `text-embedding-3-small` 모델
- 215개 질병 데이터 저장

### 3. GRADE 노드 (관련성 평가)

**역할:** 검색된 문서의 관련성을 LLM으로 평가

```
입력: documents, question
처리:
  각 문서에 대해 "이 문서가 질문과 관련있는가?" 평가
  
  평가 결과:
  - "yes" → filtered_documents에 추가
  - "no" → 제외
  
  filtered_documents가 비어있으면:
    web_search_needed = "Yes"
  아니면:
    web_search_needed = "No"

출력: filtered_documents, web_search_needed
```

**평가 기준:**
- 엄격하지 않게 평가
- 약간의 연관성도 있으면 관련있음 판정
- 완전히 무관하면만 제외

### 4. WEB_SEARCH 노드 (웹 검색)

**역할:** Tavily API로 웹 검색 수행

```
입력: question, (웹 검색 필요 시만 실행)
처리:
  - Tavily API로 웹 검색
  - 상위 3개 결과 반환
  - Document 객체로 변환
  - 기존 문서에 병합

출력: filtered_documents (내부 + 웹 검색 문서)
```

**Tavily 특징:**
- 실시간 웹 검색
- 최신 정보 제공
- 신뢰할 수 있는 출처 우선

### 5. GENERATE 노드 (답변 생성)

**역할:** 최종 답변 생성

```
입력: question, filtered_documents, classification
처리:
  1. 컨텍스트 구성 (문서 내용 + 출처)
  2. 프롬프트 선택 (분류별 다른 시스템 프롬프트)
  3. LLM 호출 (gpt-4o-mini)
  4. 답변 생성

출력: answer, sources, context
```

**분류별 프롬프트:**
- `medical` - 의료 전문가 역할
- `hospital` - 병원 안내 전문가
- `general` - 친절한 정보 제공자

---

## 💡 조건부 로직

### GRADE → GENERATE/WEB_SEARCH 결정

```python
def decide_to_generate(state):
    if classification != "medical":
        return "generate"  # 의료 질문 아님
    
    if web_search_needed == "Yes":
        return "web_search"  # 내부 문서 부족
    else:
        return "generate"  # 내부 문서 충분
```

---

## 📈 데이터 흐름

```
질병 JSON 파일들
   ↓
문서 로드 (215개)
   ↓
텍스트 분할 (청크)
   ↓
임베딩 생성
   ↓
Chroma 벡터 저장소
   ↓
retriever 객체
   ↓
(런타임)
사용자 질문
   ↓
StateGraph 실행
   ↓
최종 답변
```

---

## 🎨 사용 사례

### 사례 1: 의료 질문 (내부 문서 충분)

```
질문: "강아지가 구토를 해요"

워크플로우:
1. CLASSIFY: medical
2. RETRIEVE: "강아지 구토" 관련 문서 검색
3. GRADE: 문서 관련성 평가 → 3개 모두 "관련있음"
4. DECISION: web_search_needed = "No" → GENERATE로
5. GENERATE: 내부 문서로 답변 생성

결과: 내부 데이터만 사용하여 빠른 답변
```

### 사례 2: 의료 질문 (내부 문서 부족)

```
질문: "최신 반려동물 백신 정보"

워크플로우:
1. CLASSIFY: medical
2. RETRIEVE: 관련 문서 검색
3. GRADE: 평가 결과 "관련없음" → web_search_needed = "Yes"
4. DECISION: WEB_SEARCH로
5. WEB_SEARCH: Tavily로 웹 검색
6. GENERATE: 내부 + 웹 검색 문서로 답변

결과: 최신 정보 포함한 답변
```

### 사례 3: 일반 질문

```
질문: "반려견과 여행할 때 주의할 점?"

워크플로우:
1. CLASSIFY: general
2. RETRIEVE: 스킵 (의료 질문 아님)
3. GRADE: 스킵
4. DECISION: 바로 GENERATE로
5. GENERATE: LLM이 직접 일반 정보 제공

결과: 빠른 일반 정보 제공
```

---

## 🔍 상세 구현

### State 정의

```python
class PetMedicalState(TypedDict):
    question: str                          # 사용자 질문
    documents: List[Document]              # 벡터 검색 결과
    filtered_documents: List[Document]     # 관련성 평가 통과
    web_search_needed: str                 # "Yes" / "No"
    context: str                           # 답변용 컨텍스트
    answer: str                            # 최종 답변
    grade_results: List[str]               # 평가 결과
    classification: str                    # 질문 분류
    sources: List[dict]                    # 출처 정보
```

### 노드 함수 구조

```python
def node_name(state: PetMedicalState) -> dict:
    """
    노드 함수 구조
    
    입력: state (현재 상태)
    출력: 업데이트할 상태 필드의 dict
    """
    # 로직
    result = {...}
    return result
```

### StateGraph 구성

```python
workflow = StateGraph(PetMedicalState)

# 노드 추가
workflow.add_node("classify", classify_question_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade_documents", grade_documents_node)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate_node)

# 엣지 추가
workflow.add_edge(START, "classify")
workflow.add_edge("classify", "retrieve")
workflow.add_edge("retrieve", "grade_documents")

# 조건부 엣지
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,  # 조건 함수
    {"generate": "generate", "web_search": "web_search"}
)

# 컴파일
app = workflow.compile()
```

### 실행

```python
initial_state = {
    "question": "질문",
    "documents": [],
    # ... 기타 필드
}

for output in app.stream(initial_state):
    # 각 노드 실행
    pass

final_state = output  # 최종 상태
```

---

## 🛠️ 커스터마이제이션

### 1. 모델 변경

`pet_medical_rag_langgraph.py`에서:

```python
# Grader LLM
grader_llm = ChatOpenAI(model="gpt-4o-mini")

# Generation LLM
generation_llm = ChatOpenAI(model="gpt-4o")

# Classification LLM
classification_llm = ChatOpenAI(model="gpt-4o-mini")
```

### 2. 검색 결과 수 조정

```python
# 리트리버 설정
retriever = vectorstore.as_retriever(search_kwargs={'k': 5})  # 3 → 5
```

### 3. 청크 크기 조정

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,        # 기본값 500
    chunk_overlap=50       # 기본값 100
)
```

### 4. 프롬프트 수정

각 노드의 `ChatPromptTemplate` 수정

---

## 📊 성능 특성

| 항목 | 값 |
|------|-----|
| 문서 수 | 215개 |
| 청크 수 | ~400개 |
| 평균 응답 시간 | 2-5초 |
| 웹 검색 시간 | 3-8초 |
| 메모리 사용 | ~500MB |
| 벡터 저장소 크기 | ~50MB |

---

## 🐛 문제 해결

### API 키 오류

```
❌ OPENAI_API_KEY 환경 변수 설정 필수

해결:
1. .env 파일 생성
2. OPENAI_API_KEY=sk-... 추가
3. 저장 후 재실행
```

### Tavily 검색 오류

```
❌ TAVILY_API_KEY 환경 변수 설정 필수

해결:
1. https://app.tavily.com 가입
2. API 키 발급
3. .env에 추가
```

### 벡터 저장소 오류

```
❌ chroma_pet_medical 디렉토리 오류

해결:
1. rm -rf chroma_pet_medical
2. 스크립트 재실행
```

---

## 🚀 고급 사용

### 프로그래매틱 사용

```python
from pet_medical_rag_langgraph import run_pet_medical_rag

result = run_pet_medical_rag("강아지 감기 증상")
```

### 커스텀 질문 처리

```python
from pet_medical_rag_langgraph import app

initial_state = {
    "question": "질문",
    "documents": [],
    "filtered_documents": [],
    # ... 기타 필드
}

for output in app.stream(initial_state):
    # 처리
    pass
```

---

## 📚 참고 자료

- **LangGraph**: https://github.com/langchain-ai/langgraph
- **LangChain**: https://python.langchain.com/
- **Tavily API**: https://tavily.com/
- **CRAG 패턴**: Corrective RAG (내부 문서 부족시 웹 검색)

---

## 💡 다음 단계

1. **병원 데이터 통합** - CSV 병원 정보 활용
2. **음성 입출력** - 음성 질문 및 답변
3. **채팅 인터페이스** - 웹 UI 추가
4. **사용자 피드백** - 답변 평가 시스템
5. **성능 최적화** - 캐싱, 배치 처리

---

**LangGraph 기반 CRAG 어시스턴트 구현 완료! 🎉**

