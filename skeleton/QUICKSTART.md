# ⚡ 스켈레톤 코드 빠른 시작 가이드

5분 안에 스켈레톤 코드를 이해하고 실행해보세요!

---

## 📋 사전 요구사항

- Python 3.9 이상
- pip 또는 conda

---

## 🚀 Step 1: 파일 구조 이해하기

```
skeleton/
├── input_classifier.py       ← 입력 분류 모듈
├── rag_handler.py            ← RAG/웹 검색 모듈
├── map_handler.py            ← 지도 정보 모듈
├── llm_generator.py          ← LLM 응답 생성 모듈
├── evaluation_controller.py  ← 평가 및 제어 모듈
├── main.py                   ← 메인 워크플로우 (모두 조합)
├── README.md                 ← 상세 문서
├── ARCHITECTURE.md           ← 아키텍처 설명
├── requirements.txt          ← 의존 패키지
└── QUICKSTART.md             ← 이 파일
```

---

## 🎯 Step 2: 각 모듈의 핵심 함수

### 1️⃣ input_classifier.py
```python
def classify_query(query: str) -> str
    # 입력: "강아지 피부 질환?"
    # 출력: "medical_consultation"
```

### 2️⃣ rag_handler.py
```python
def perform_rag_search(query: str) -> str
def perform_web_search(query: str) -> str
def search_with_fallback(query: str) -> tuple[str, str]
    # 입력: "강아지 증상?"
    # 출력: ("검색된 문서 텍스트...", "rag" 또는 "web")
```

### 3️⃣ map_handler.py
```python
def get_map_info(query: str) -> str
    # 입력: "근처 동물병원 찾아줘"
    # 출력: "병원 정보...\n주소: ...\n전화: ..."
```

### 4️⃣ llm_generator.py
```python
def generate_response(query: str, context: str) -> str
def rewrite_response(response: str, feedback: str) -> str
    # 입력: 쿼리 + 컨텍스트
    # 출력: "생성된 답변..."
```

### 5️⃣ evaluation_controller.py
```python
def evaluate_response(response: str) -> dict
    # 입력: "생성된 답변..."
    # 출력: {
    #   'pass': True/False,
    #   'scores': {'accuracy': 0.85, 'clarity': 0.90, ...},
    #   'feedback': '평가 피드백'
    # }
```

### 6️⃣ main.py
```python
def main_workflow(query: str) -> str
    # 입력: "강아지 피부 질환 증상?"
    # 출력: "최종 답변..."
```

---

## 💻 Step 3: 기본 사용 예제

### 예제 1: 단일 쿼리 처리 (가장 간단)

```python
from main import main_workflow

# 사용자 쿼리 입력
query = "강아지 피부 질환 증상이 뭐예요?"

# 워크플로우 실행 (모든 모듈 자동 호출)
response = main_workflow(query)

# 결과 출력
print(f"질문: {query}")
print(f"답변: {response}")
```

**실행 결과:**
```
============================================================
🚀 메인 워크플로우 시작
============================================================
📝 사용자 쿼리: 강아지 피부 질환 증상이 뭐예요?
============================================================

📊 [스텝 1] 입력 쿼리 분류...
   ✓ 분류 결과: medical_consultation

🔍 [스텝 2] 정보 검색...
   ✓ RAG 검색 성공
   📚 컨텍스트 길이: 1234 문자

💡 [스텝 3] 시스템 프롬프트 구성...
   ✓ 프롬프트 구성 완료

🤖 [스텝 4] LLM 응답 생성...
   ✓ 초기 응답 생성 완료
   📄 응답 길이: 567 문자

⚖️  [스텝 5] 응답 평가 및 재작성 루프...

   📊 평가 결과 (시도 #1):
      - 정확도 (Accuracy): 85.00%
      - 명확성 (Clarity): 90.00%
      - 완전성 (Completeness): 80.00%
      - 안전성 (Safety): 88.00%
      - 평균 점수: 85.75%
      - 피드백: 응답이 적절합니다...
   ✅ 평가 통과! 응답 승인

📈 [스텝 6] 최종 메트릭:
   - 총 처리 시간: 2.34초
   - 재작성 횟수: 0회
   - 최종 평가 점수: 85.75%
   - 평가 통과: ✓

============================================================
✨ 최종 답변 반환
============================================================

최종 답변:
[생성된 답변]
...
```

---

### 예제 2: 특정 모듈만 사용

```python
# 1. 입력 분류만 수행
from input_classifier import classify_query

query = "서울 강남역 근처 동물병원 찾아줘"
query_type = classify_query(query)
print(f"분류: {query_type}")
# 출력: map_search


# 2. 검색만 수행
from rag_handler import search_with_fallback

context, source = search_with_fallback("강아지 증상?")
print(f"검색 소스: {source}")
print(f"결과 길이: {len(context)} 문자")
# 출력: 
# 검색 소스: rag
# 결과 길이: 1234 문자


# 3. LLM 응답 생성만 수행
from llm_generator import generate_response

response = generate_response(
    query="강아지 피부 증상?",
    context="피부 질환 관련 문서..."
)
print(f"답변: {response}")


# 4. 평가만 수행
from evaluation_controller import evaluate_response

evaluation = evaluate_response("생성된 답변...")
print(f"점수: {evaluation['average_score']:.2%}")
print(f"통과: {evaluation['pass']}")
```

---

### 예제 3: 배치 처리 (여러 쿼리)

```python
from main import batch_workflow

queries = [
    "강아지 피부 질환 증상?",
    "서울 강남역 근처 동물병원 찾아줘",
    "반려동물 예방 접종은 언제 해야 하나요?",
    "고양이 귀 감염 치료법?"
]

# 배치 처리 실행
results = batch_workflow(queries)

# 결과 확인
for result in results:
    print(f"질문: {result['query']}")
    print(f"분류: {result['query_type']}")
    print(f"처리 시간: {result['processing_time']:.2f}초")
    print(f"평가 점수: {result['evaluation_score']:.2%}")
    print("---")
```

---

## 🔄 Step 4: 워크플로우 이해하기

### 전체 흐름 (한 눈에)

```
사용자 입력
    ↓
1️⃣  분류 (medical? map? general?)
    ↓
2️⃣  검색 (RAG 또는 웹 또는 지도)
    ↓
3️⃣  생성 (LLM으로 답변 생성)
    ↓
4️⃣  평가 (4개 지표로 품질 평가)
    ↓
5️⃣  결정 (accept? rewrite? escalate?)
    ↓
6️⃣  최종 답변 반환
```

### 의료 상담 경로

```
"강아지 피부 질환?"
    ↓
분류: medical_consultation
    ↓
RAG 검색 (의료 문서)
    ↓
프롬프트: "당신은 반려동물 의료 전문가입니다..."
    ↓
LLM 응답 생성
    ↓
평가:
  - 정확도 ✓
  - 명확성 ✓
  - 완전성 ✓
  - 안전성 ✓ (면책 조항 포함)
    ↓
✅ 최종 답변 반환
```

### 지도 검색 경로

```
"근처 동물병원"
    ↓
분류: map_search
    ↓
지도 API 조회
    ↓
병원 정보:
  - 병원명
  - 주소
  - 전화
  - 영업시간
    ↓
✅ 최종 답변 반환
```

---

## 📊 Step 5: 평가 점수 해석

### 평가 4개 차원

| 지표 | 범위 | 의미 |
|------|------|------|
| 정확도 (Accuracy) | 0.0-1.0 | 정보가 맞나? |
| 명확성 (Clarity) | 0.0-1.0 | 이해하기 쉬운가? |
| 완전성 (Completeness) | 0.0-1.0 | 충분한가? |
| 안전성 (Safety) | 0.0-1.0 | 의료 조언이 안전한가? |

### 다음 액션 결정

```
평균 점수 = (정확도 + 명확성 + 완전성 + 안전성) / 4

✅ Accept (점수 ≥ 0.75)
   → 응답을 그대로 사용자에게 전달

🔄 Rewrite (0.50 ≤ 점수 < 0.75)
   → 피드백을 반영하여 재작성 (최대 2회)

⚠️  Escalate (점수 < 0.50)
   → 인간 검토 또는 에러 처리
```

---

## 🛠️ Step 6: 스켈레톤 → 구현하기

### Phase 1: 기본 구현
각 모듈에 `# TODO` 주석을 따라 구현하세요.

```python
# 예: input_classifier.py
def classify_query(query: str) -> str:
    # TODO: 실제 LLM 또는 전용 분류 모델 호출
    # 지금: 키워드 매칭 (더미 구현)
    # 나중: LLM 기반 분류 (실제 구현)
```

### Phase 2: API 연결
```python
# 예: rag_handler.py
# TODO: OpenAI Embeddings로 쿼리 임베딩
# TODO: Chroma DB에서 유사 문서 검색
# TODO: LLM으로 관련성 평가
# TODO: Tavily API로 웹 검색
```

### Phase 3: 통합 테스트
```bash
python main.py  # 테스트 쿼리 3개 실행
```

---

## 🔗 다음 단계

1. **README.md** - 상세 문서 읽기
2. **ARCHITECTURE.md** - 아키텍처 이해하기
3. **각 모듈 구현** - TODO 주석 따라 구현
4. **테스트** - main.py 테스트 코드 실행
5. **통합** - 기존 프로젝트와 연계

---

## ❓ FAQ

### Q1: 스켈레톤 코드를 어떻게 실행하나요?
**A:** `main.py`에 테스트 코드가 포함되어 있습니다.
```bash
cd skeleton
python main.py
```

### Q2: 각 모듈은 독립적으로 사용 가능한가요?
**A:** 네! 각 모듈은 독립적입니다.
```python
from input_classifier import classify_query
query_type = classify_query("강아지 증상?")
```

### Q3: 실제 LLM은 언제 연결하나요?
**A:** `llm_generator.py`의 TODO를 따라 OpenAI API를 연결하세요.

### Q4: 벡터 DB는 어디서 준비하나요?
**A:** 기존 프로젝트의 `chroma_db` 디렉토리를 사용하거나, 데이터를 다시 로드하세요.

### Q5: 웹 검색 API를 설정하려면?
**A:** Tavily API 키를 `.env` 파일에 추가하세요:
```
TAVILY_API_KEY=your-key-here
```

---

## 📚 추가 자료

- [README.md](./README.md) - 전체 문서
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 아키텍처 상세
- [requirements.txt](./requirements.txt) - 의존 패키지

---

**팁:** 
- 🎯 **한 번에 한 모듈씩** 구현하세요
- 🧪 **각 단계마다 테스트**하세요
- 📝 **로깅을 추가**하여 디버깅을 쉽게 하세요
- 🔄 **반복적으로 개선**하세요

---

**작성일**: 2025-12-05  
**버전**: 0.1.0

