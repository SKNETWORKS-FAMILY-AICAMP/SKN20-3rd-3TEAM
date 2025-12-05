# 🏥 RAG 어시스턴트 스켈레톤 코드

기존의 복잡한 RAG 시스템을 **6개의 핵심 모듈**로 단순화한 스켈레톤 코드입니다.  
각 모듈은 함수/클래스 시그니처와 주석만 포함하며, 실제 구현은 생략되어 있습니다.

---

## 📚 모듈 구조

### 1️⃣ `input_classifier.py` - 입력 분류
**목표**: 사용자 쿼리를 의도에 따라 분류

```python
def classify_query(query: str) -> Literal["medical_consultation", "map_search", "general"]
```

| 분류 | 설명 | 예시 |
|------|------|------|
| `medical_consultation` | 의료 상담 | "강아지 피부 질환 증상?" |
| `map_search` | 지도/병원 검색 | "근처 동물병원 찾아줘" |
| `general` | 일반 질문 | "반려동물 키우기 팁" |

**핵심 로직**:
- 간단한 키워드 매칭 (프로덕션: LLM 기반)
- 반환값: 분류 카테고리 문자열

---

### 2️⃣ `rag_handler.py` - RAG 및 웹 검색
**목표**: 벡터 DB 또는 웹에서 관련 정보 검색

```python
def perform_rag_search(query: str) -> str           # RAG 검색
def perform_web_search(query: str) -> str           # 웹 검색
def search_with_fallback(query: str) -> tuple[str, str]  # RAG → 웹 폴백
```

**CRAG 패턴 (Corrective RAG)**:
```
[쿼리] → [RAG 검색] → [관련성 평가]
                        ↓
                    충분? 
                   /     \
                 YES     NO
                  ↓       ↓
              사용    [웹 검색]
                        ↓
                    [최종 컨텍스트]
```

**반환값**: 검색된 문서/웹 결과 텍스트

---

### 3️⃣ `map_handler.py` - 지도/병원 정보
**목표**: 병원 위치, 영업시간 등 지도 정보 제공

```python
def get_map_info(query: str) -> str                 # 병원 정보 검색
def extract_hospital_name(query: str) -> Optional[str]  # 병원명 추출
def extract_location(query: str) -> Optional[str]       # 위치 정보 추출
```

**반환 정보**:
- 병원명
- 주소
- 전화번호
- 영업시간
- 거리 정보

**워크플로우**:
1. 쿼리에서 위치/병원명 추출
2. 지도 API (카카오맵) 또는 로컬 DB 검색
3. 구조화된 병원 정보 반환

---

### 4️⃣ `llm_generator.py` - LLM 응답 생성
**목표**: 쿼리와 컨텍스트를 바탕으로 답변 생성

```python
def generate_response(query: str, context: str) -> str
def rewrite_response(response: str, feedback: str) -> str
def build_system_prompt(query_type: str) -> str
```

**프롬프트 엔지니어링**:
- 질문 유형별 시스템 프롬프트 구성
- 컨텍스트 주입 (RAG/웹 검색 결과)
- 응답 제약 조건 설정

**반환값**: LLM이 생성한 최종 답변 텍스트

---

### 5️⃣ `evaluation_controller.py` - 응답 평가
**목표**: 생성된 응답의 품질 평가 및 흐름 제어

```python
def evaluate_response(response: str) -> Dict[str, any]
def check_safety_guidelines(response: str) -> Dict[str, any]
def determine_next_action(response: str, evaluation: Dict) -> Literal["accept", "rewrite", "escalate"]
```

**평가 기준** (4개 차원):

| 항목 | 기준 | 설명 |
|------|------|------|
| 정확도 (Accuracy) | 0.0-1.0 | 정보가 정확한가? |
| 명확성 (Clarity) | 0.0-1.0 | 설명이 명확한가? |
| 완전성 (Completeness) | 0.0-1.0 | 충분하게 답변했는가? |
| 안전성 (Safety) | 0.0-1.0 | 의료 조언이 안전한가? |

**반환값**: 
```python
{
    'pass': True/False,                    # 평가 통과
    'feedback': '개선 필요 사항',           # 피드백
    'scores': {
        'accuracy': 0.85,
        'clarity': 0.90,
        'completeness': 0.80,
        'safety': 0.88
    },
    'reason': '평가 근거'
}
```

**다음 액션 결정**:
- ✅ **Accept** (점수 ≥ 75%): 응답 승인
- 🔄 **Rewrite** (50%-75%): 피드백 반영 재작성
- ⚠️ **Escalate** (점수 < 50%): 인간 검토 필요

---

### 6️⃣ `main.py` - 워크플로우 오케스트레이션
**목표**: 5개 모듈을 조합하여 엔드-투-엔드 처리

```python
def main_workflow(query: str, max_rewrite_attempts: int = 2) -> str
def main_workflow_with_feedback(query: str, user_feedback: str) -> str
def batch_workflow(queries: list[str]) -> list[Dict[str, any]]
```

**엔드-투-엔드 워크플로우**:

```
사용자 쿼리
    ↓
1️⃣ [분류] classify_query()
    ↓
2️⃣ [검색] search_with_fallback() 또는 get_map_info()
    ↓
3️⃣ [생성] generate_response()
    ↓
4️⃣ [평가] evaluate_response()
    ↓
5️⃣ [재작성 루프] (필요시)
    ↓
✅ [최종 답변] 반환
```

---

## 🚀 사용 방법

### 기본 사용 (단일 쿼리)
```python
from main import main_workflow

query = "강아지 피부 질환 증상이 뭐예요?"
response = main_workflow(query)
print(response)
```

### 사용자 피드백 포함
```python
from main import main_workflow_with_feedback

response = main_workflow_with_feedback(
    query="강아지 피부 질환 증상?",
    user_feedback="더 짧게 설명해줄 수 있어?"
)
```

### 배치 처리 (여러 쿼리)
```python
from main import batch_workflow

queries = [
    "강아지 피부 질환 증상?",
    "서울 강남역 근처 동물병원 찾아줘",
    "반려동물 예방 접종 시기?"
]

results = batch_workflow(queries)
for result in results:
    print(f"질문: {result['query']}")
    print(f"분류: {result['query_type']}")
    print(f"점수: {result['evaluation_score']:.2%}")
```

---

## 📊 데이터 흐름

### 의료 상담 경로
```
"강아지 피부 질환 증상?"
    ↓
🏷️  분류: medical_consultation
    ↓
🔍 RAG 검색 (의료 문서)
    ↓
💬 의료 전문가 프롬프트 적용
    ↓
🤖 LLM 응답 생성
    ↓
🛡️  안전성 검증 (면책 조항 포함?)
    ↓
⚖️  평가 (정확도, 명확성, 완전성, 안전성)
    ↓
✨ 최종 답변
```

### 지도 검색 경로
```
"근처 동물병원 찾아줘"
    ↓
🏷️  분류: map_search
    ↓
🗺️  지도 API 조회 (병원 정보)
    ↓
📍 병원명, 주소, 전화 추출
    ↓
💬 포맷팅 및 정렬
    ↓
🤖 LLM으로 최종 포맷팅
    ↓
⚖️  평가 및 검증
    ↓
✨ 최종 답변
```

---

## 🔧 모듈별 함수 시그니처

### input_classifier.py
```python
classify_query(query: str) 
  → Literal["medical_consultation", "map_search", "general"]
```

### rag_handler.py
```python
perform_rag_search(query: str) → str
perform_web_search(query: str) → str
search_with_fallback(query: str) → tuple[str, str]
```

### map_handler.py
```python
get_map_info(query: str) → str
extract_hospital_name(query: str) → Optional[str]
extract_location(query: str) → Optional[str]
format_map_response(hospitals: list[dict]) → str
```

### llm_generator.py
```python
generate_response(query: str, context: str) → str
rewrite_response(response: str, feedback: str) → str
build_system_prompt(query_type: str) → str
estimate_token_count(text: str) → int
truncate_context(context: str, max_length: int) → str
```

### evaluation_controller.py
```python
evaluate_response(response: str) → Dict[str, any]
check_safety_guidelines(response: str) → Dict[str, any]
check_factual_accuracy(response: str, context: str) → Dict[str, any]
determine_next_action(response: str, evaluation: Dict) 
  → Literal["accept", "rewrite", "escalate"]
collect_evaluation_metrics(...) → Dict[str, any]
```

### main.py
```python
main_workflow(query: str, max_rewrite_attempts: int) → str
main_workflow_with_feedback(query: str, user_feedback: str) → str
batch_workflow(queries: list[str]) → list[Dict[str, any]]
```

---

## 📝 스켈레톤 코드 특징

✅ **함수/클래스 시그니처만 정의** - 구현 로직 없음  
✅ **상세한 주석** - 각 함수의 목적, 입출력, 워크플로우 명시  
✅ **더미 데이터 반환** - 실제 동작 가능 (테스트용)  
✅ **모듈 독립성** - 각 모듈은 독립적으로 사용 가능  
✅ **타입 힌팅** - 함수 시그니처의 명확성  
✅ **에러 처리 기본 구조** - TODO 주석으로 구현 위치 표시  

---

## 🎯 다음 단계 (구현)

각 모듈의 TODO 주석을 따라 다음과 같이 구현하세요:

### 1. `input_classifier.py`
- [ ] LLM 또는 전용 분류 모델 연결
- [ ] 키워드 가중치 조정

### 2. `rag_handler.py`
- [ ] 벡터 DB (Chroma) 연결
- [ ] 임베딩 모델 통합
- [ ] 웹 검색 API (Tavily) 통합

### 3. `map_handler.py`
- [ ] 카카오맵 API 연결
- [ ] 병원 데이터베이스 로드
- [ ] 거리 기반 필터링 구현

### 4. `llm_generator.py`
- [ ] OpenAI GPT API 연결
- [ ] 프롬프트 템플릿 개선
- [ ] 토큰 비용 계산

### 5. `evaluation_controller.py`
- [ ] LLM 기반 평가 로직
- [ ] 안전성 검증 구현
- [ ] 할루시네이션 감지

### 6. `main.py`
- [ ] 에러 핸들링 추가
- [ ] 로깅 시스템 통합
- [ ] 성능 모니터링

---

## 📂 파일 구조

```
skeleton/
├── input_classifier.py      # 입력 분류
├── rag_handler.py           # RAG/웹 검색
├── map_handler.py           # 지도 정보
├── llm_generator.py         # LLM 응답 생성
├── evaluation_controller.py # 평가 및 제어
├── main.py                  # 워크플로우 오케스트레이션
└── README.md                # 이 문서
```

---

## 🔗 기존 프로젝트와의 연계

이 스켈레톤 코드는 다음 기존 코드를 참고하여 작성되었습니다:

- `src/question_classifier.py` → `input_classifier.py`
- `src/pipeline.py` → `rag_handler.py` + `main.py`
- `src/kakao_map.py` → `map_handler.py`
- `src/llm/client.py` → `llm_generator.py`
- 새로 추가됨 → `evaluation_controller.py`

---

## 💡 팁

1. **점진적 구현**: 한 번에 한 모듈씩 구현하세요.
2. **테스트 우선**: 각 모듈의 반환값 형태를 먼저 정하세요.
3. **통합 테스트**: `main.py`의 테스트 코드를 실행하며 진행하세요.
4. **로깅 추가**: 각 단계의 중간 결과를 로깅하여 디버깅을 쉽게 하세요.

---

**작성일**: 2025-12-05  
**버전**: 0.1.0 (스켈레톤)  
**라이선스**: 교육/연구 목적

