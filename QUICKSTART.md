# 빠른 시작 가이드

## 🚀 설치 및 초기 설정

### 1. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 다음을 추가하세요:

```bash
# OpenAI API 설정
OPENAI_API_KEY=sk-...
LOG_LEVEL=INFO

# 웹 검색 (선택사항)
TAVILY_API_KEY=tvly-...

# 카카오맵 API (선택사항)
KAKAO_MAP_API_KEY=...

# 디버그 모드 (선택사항)
DEBUG_MODE=False
```

### 2. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 📖 기본 사용법

### 방법 1: 간단한 한 줄 사용

```python
from src import RAGOrchestrator, load_vectorstore, get_embedding_model

# 벡터스토어 로드
embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model, persist_directory="./chroma_db")

# 오케스트레이터 생성
orchestrator = RAGOrchestrator(vectorstore=vectorstore)

# 질문 처리
result = orchestrator.process("강아지 피부염의 증상은?")
print(result['formatted_answer'])
```

### 방법 2: 대화형 모드

```python
from src import RAGOrchestrator, load_vectorstore, get_embedding_model

embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model)
orchestrator = RAGOrchestrator(vectorstore=vectorstore)

# 대화형 시작
orchestrator.interactive_mode()
```

### 방법 3: 배치 처리

```python
questions = [
    "강아지 설사 증상은?",
    "강남역 근처 동물병원",
    "반려견 영양 관리",
]

results = orchestrator.batch_process(questions)
orchestrator.save_results(results, output_path="results.json")
```

---

## 🏥 질문 유형별 예시

### 1️⃣ 의료 질문 (Type A)
자동으로 내부 벡터스토어에서 검색하고, 필요시 웹 검색

```python
result = orchestrator.process("강아지 귀염증 원인과 치료법은?")
# 결과:
# - 내부 문서 검색
# - 근거 점수 평가
# - LLM 기반 답변 생성
# - 출처 표시
```

### 2️⃣ 병원/지도 질문 (Type B)
자동으로 병원 DB에서 검색하고 지도 표시

```python
result = orchestrator.process("강남역 근처 동물병원 어디 있어?")
# 또는 좌표 기반:
result = orchestrator.process(
    "근처 병원",
    latitude=37.4979,
    longitude=127.0276
)
# 결과:
# - 병원 정보 조회
# - 거리 기반 정렬
# - 카카오맵 HTML 생성
```

### 3️⃣ 일반 질문 (Type C)
LLM이 직접 답변

```python
result = orchestrator.process("반려견 훈련 팁을 알려주세요")
# 결과:
# - LLM 기반 일반 답변
# - 내부 검색 없음
```

---

## 📊 결과 이해하기

### 결과 구조

```python
result = {
    'question': str,                    # 원본 질문
    'question_type': str,              # 'A', 'B', 'C'
    'timestamp': str,                  # ISO 형식 시간
    'classification_confidence': float, # 분류 신뢰도
    'classification_type': str,        # 'MEDICAL', 'HOSPITAL', 'GENERAL'
    'classification_reason': str,      # 분류 이유
    'answer': str,                     # 답변 (의료/일반용)
    'response': str,                   # 응답 (병원용)
    'sources': list,                   # 출처 정보
    'formatted_answer': str,           # 포맷된 최종 답변
    
    # 의료 질문 전용
    'internal_search_results': int,    # 내부 검색 결과 수
    'web_search_results': int,         # 웹 검색 결과 수
    'relevance_score': float,          # 근거 충분도 점수
    'used_web_search': bool,           # 웹 검색 사용 여부
    
    # 병원 질문 전용
    'hospitals': list,                 # 병원 정보 리스트
}
```

### 의료 질문 결과 예시

```python
{
    'question': '강아지 피부염 증상은?',
    'question_type': 'A',
    'answer': '강아지 피부염의 일반적인 증상은...',
    'relevance_score': 0.85,
    'internal_search_results': 5,
    'web_search_results': 0,
    'used_web_search': False,
    'sources': [
        {
            'content': '...',
            'metadata': {
                'file_name': 'medical_01.json',
                'department': '피부과'
            },
            'relevance_score': 0.92
        }
    ],
    'formatted_answer': '...'
}
```

---

## 🔧 주요 설정 옵션

### RAGOrchestrator 설정

```python
orchestrator = RAGOrchestrator(
    vectorstore=vectorstore,           # Chroma 벡터스토어
    hospital_json_path="...",         # 병원 JSON 경로
    llm_model="gpt-4o-mini",          # LLM 모델
    score_threshold=0.6               # 의료 질문 신뢰도 임계값
)
```

### 임베딩 모델 선택

```python
# OpenAI 모델 (기본)
embedding = get_embedding_model("openai", model_name="text-embedding-3-small")

# HuggingFace 모델 (로컬)
embedding = get_embedding_model("huggingface", model_name="jhgan/ko-sroberta-multitask")
```

### 전역 설정 커스터마이즈

```python
from src.config import Settings, LLMConfig, RetrieverConfig

settings = Settings(
    llm=LLMConfig(model="gpt-4", temperature=0.5),
    retriever=RetrieverConfig(top_k=10, score_threshold=0.5)
)
```

---

## 🎯 성능 팁

### 1. 캐싱 활용
```python
from src.llm import get_llm_client
llm = get_llm_client()  # 첫 호출: 생성
llm = get_llm_client()  # 두 번째 호출: 캐시된 인스턴스 반환
```

### 2. 배치 처리 최적화
```python
# 많은 질문을 한 번에 처리
results = orchestrator.batch_process(
    questions,  # 리스트
    **kwargs    # 공통 파라미터
)
```

### 3. 커스텀 검색 옵션
```python
result = orchestrator.process(
    query,
    latitude=37.49,        # 병원 검색용
    longitude=127.02,
)
```

---

## 📁 데이터 준비

### 벡터스토어 생성 (처음 한 번)

```python
from src import ingest_data, chunk_documents_with_token_range
from src import get_embedding_model, create_vectorstore

# 데이터 로드 및 청킹
documents = ingest_data("data/raw")
chunked_docs = chunk_documents_with_token_range(documents)

# 임베딩 및 벡터스토어 생성
embedding_model = get_embedding_model("openai")
vectorstore = create_vectorstore(
    documents=chunked_docs,
    embedding_model=embedding_model,
    persist_directory="./chroma_db"
)
```

### 병원 데이터 설정

병원 JSON 파일을 다음 경로에 배치하세요:
```
data/raw/hospital/서울시_동물병원_인허가_정보.json
```

또는 직접 지정:
```python
orchestrator = RAGOrchestrator(
    vectorstore=vectorstore,
    hospital_json_path="/path/to/hospital.json"
)
```

---

## 🐛 트러블슈팅

### OpenAI API 에러
```
ValueError: OPENAI_API_KEY 환경변수가 설정되지 않았습니다
```
**해결**: `.env` 파일에 `OPENAI_API_KEY` 추가

### 벡터스토어 로드 실패
```
FileNotFoundError: chroma_db not found
```
**해결**: 벡터스토어 생성 후 사용 (위 "데이터 준비" 참고)

### 병원 데이터 로드 실패
```
병원 데이터 로드 완료: 0개 병원
```
**해결**: 병원 JSON 파일 경로 확인

### 웹 검색 미작동
```
Tavily API 키가 설정되지 않았습니다
```
**해결**: `.env`에 `TAVILY_API_KEY` 추가 (선택사항)

---

## 📚 더 읽을 거리

- [아키텍처 가이드](./ARCHITECTURE.md) - 전체 시스템 설계
- [모듈 문서](#) - 각 모듈 상세 설명 (작성 예정)
- [API 레퍼런스](#) - 함수/클래스 상세 문서 (작성 예정)

---

## 💬 예제 코드

### 예제 1: 의료 상담

```python
from src import RAGOrchestrator, load_vectorstore, get_embedding_model

def medical_consultation():
    # 초기화
    embedding_model = get_embedding_model("openai")
    vectorstore = load_vectorstore(embedding_model)
    orchestrator = RAGOrchestrator(vectorstore=vectorstore)
    
    # 상담 질문들
    questions = [
        "강아지가 계속 물린다고 긁어요. 어떻게 되는 걸까요?",
        "피부염 진단받은 후 어떤 약을 쓰나요?",
        "치료 기간은 얼마나 걸리나요?"
    ]
    
    for q in questions:
        result = orchestrator.process(q)
        print(f"\n질문: {q}")
        print(f"답변: {result['formatted_answer']}")
        print(f"신뢰도: {result.get('relevance_score', 'N/A')}")

medical_consultation()
```

### 예제 2: 병원 검색

```python
def find_hospitals():
    orchestrator = RAGOrchestrator(vectorstore=vectorstore)
    
    result = orchestrator.process(
        "강남구 역삼동 근처 동물병원",
        location="강남구"
    )
    
    print(f"검색 결과: {result['response']}")
    for hospital in result['hospitals'][:3]:
        print(f"- {hospital['name']}: {hospital['phone']}")

find_hospitals()
```

---

**다음 단계**: 아키텍처 가이드를 읽고 각 모듈의 역할을 이해해보세요!

