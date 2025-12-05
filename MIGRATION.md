# 마이그레이션 가이드 - 기존 코드에서 새 구조로

## 📝 개요

이 가이드는 기존의 단일 파일 구조에서 책임분리(SoC) 기반의 모듈 구조로 전환하는 방법을 설명합니다.

---

## 🔄 주요 변경 사항

| 구분 | 이전 | 이후 |
|------|------|------|
| **구조** | `advanced_rag_pipeline.py` (단일 파일) | 모듈식 구조 |
| **설정** | 환경변수 분산 | `config/settings.py` 통합 |
| **검색** | 고정된 검색 로직 | `InternalSearcher`, `WebSearcher` |
| **분류** | `question_classifier.py` | `classifiers/question_classifier.py` |
| **처리** | `medical_qa_handler.py`, `hospital_handler.py` | `handlers/*` |
| **오케스트레이션** | `AdvancedRAGPipeline` | `RAGOrchestrator` |
| **재사용성** | 제한적 | 높음 (인터페이스 기반) |

---

## 🎯 마이그레이션 단계별 가이드

### 1단계: 기존 코드 분석 및 매핑

#### 이전 구조
```python
# advanced_rag_pipeline.py
class AdvancedRAGPipeline:
    def __init__(self, vectorstore, hospital_json_path, llm_model, score_threshold):
        self.vectorstore = vectorstore
        self.classifier = QuestionClassifier(llm_model)
        self.medical_handler = MedicalQAHandler(vectorstore, llm_model, score_threshold)
        self.hospital_handler = HospitalHandler(hospital_json_path)
    
    def process_question(self, query):
        # 분류 → 라우팅 → 처리
```

#### 새로운 구조
```python
# pipelines/orchestrator.py
class RAGOrchestrator(BasePipeline):
    def __init__(self, vectorstore, hospital_json_path, llm_model, score_threshold):
        self.classifier = QuestionClassifier(llm_model)
        self.medical_handler = MedicalHandler(vectorstore, llm_model=llm_model, ...)
        self.hospital_handler = HospitalHandler(hospital_json_path)
    
    def process(self, query, **kwargs):
        # 분류 → 라우팅 → 처리
```

### 2단계: Import 문 변경

#### 이전
```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline
from src.question_classifier import QuestionClassifier, QuestionType
from src.medical_qa_handler import MedicalQAHandler
from src.hospital_handler import HospitalHandler
from src.embeddings import get_embedding_model, load_vectorstore
```

#### 이후
```python
from src import (
    RAGOrchestrator,
    QuestionClassifier,
    QuestionType,
    MedicalHandler,
    HospitalHandler,
    get_embedding_model,
    load_vectorstore
)
```

또는 세분화된 import
```python
from src.pipelines import RAGOrchestrator
from src.classifiers import QuestionClassifier, QuestionType
from src.handlers import MedicalHandler, HospitalHandler
from src.core import get_embedding_model, load_vectorstore
```

### 3단계: 기본 사용법 변경

#### 이전
```python
from src.embeddings import get_embedding_model, load_vectorstore
from src.advanced_rag_pipeline import AdvancedRAGPipeline

embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model)

# AdvancedRAGPipeline 인스턴스 생성
pipeline = AdvancedRAGPipeline(
    vectorstore=vectorstore,
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json",
    llm_model="gpt-4o-mini",
    score_threshold=0.6
)

# 질문 처리
result = pipeline.process_question("강아지 피부염 증상은?")
```

#### 이후
```python
from src import (
    RAGOrchestrator,
    get_embedding_model,
    load_vectorstore
)

embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model)

# RAGOrchestrator 인스턴스 생성
orchestrator = RAGOrchestrator(
    vectorstore=vectorstore,
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json",
    llm_model="gpt-4o-mini",
    score_threshold=0.6
)

# 질문 처리
result = orchestrator.process("강아지 피부염 증상은?")
```

### 4단계: 메서드/속성 매핑

| 이전 메서드 | 새로운 메서드 | 변경 사항 |
|----------|-----------|---------|
| `process_question(query)` | `process(query)` | 없음 |
| `interactive_mode()` | `interactive_mode()` | 호환성 유지 |
| `batch_process_questions(questions)` | `batch_process(queries)` | 인자명 변경 |
| `save_results(results, path)` | `save_results(results, path)` | 호환성 유지 |

### 5단계: 결과 구조 변경 확인

#### 이전 결과 구조
```python
result = {
    'question': str,
    'question_type': str,
    'timestamp': str,
    'answer': str,
    'sources': list,
    'formatted_answer': str,
    # ... 기타 필드
}
```

#### 새로운 결과 구조 (호환성 유지)
```python
result = {
    'question': str,
    'question_type': str,
    'timestamp': str,
    'answer': str,
    'sources': list,
    'formatted_answer': str,
    'classification_type': str,         # 새로 추가
    'classification_reason': str,       # 새로 추가
    'classification_confidence': float, # 새로 추가
    # ... 기타 필드
}
```

### 6단계: 설정 마이그레이션

#### 이전
```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# ... 여러 환경변수
```

#### 이후
```python
from src.config import get_settings
from dotenv import load_dotenv

load_dotenv()

settings = get_settings()
print(settings.llm.model)           # "gpt-4o-mini"
print(settings.llm.api_key)         # 자동 로드
print(settings.external_api.tavily_api_key)
```

---

## 🔌 세부 마이그레이션

### MedicalQAHandler → MedicalHandler

#### 이전
```python
handler = MedicalQAHandler(
    vectorstore=vectorstore,
    llm_model="gpt-4o-mini",
    score_threshold=0.6,
    top_k=5
)

result = handler.handle_medical_question("피부염 증상?")
```

#### 이후
```python
handler = MedicalHandler(
    vectorstore=vectorstore,
    llm_model="gpt-4o-mini",
    score_threshold=0.6,
    top_k=5
)

result = handler.handle("피부염 증상?")

# 또는 외부 검색기 지정
from src.retrievers import InternalSearcher, WebSearcher

internal_searcher = InternalSearcher(vectorstore, top_k=5)
web_searcher = WebSearcher()

handler = MedicalHandler(
    vectorstore=vectorstore,
    internal_searcher=internal_searcher,
    web_searcher=web_searcher
)
```

### QuestionClassifier

#### 이전
```python
classifier = QuestionClassifier(llm_model="gpt-4o-mini")
question_type, confidence, reason = classifier.classify(query)
```

#### 이후
```python
from src.classifiers import QuestionClassifier

classifier = QuestionClassifier(llm_model="gpt-4o-mini")
question_type, confidence, reason = classifier.classify(query)

# 호환성 완벽 유지
print(question_type.name)  # "MEDICAL", "HOSPITAL", "GENERAL"
```

### HospitalHandler

#### 이전
```python
handler = HospitalHandler(
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json"
)

result = handler.handle_hospital_question("강남구 동물병원?")
```

#### 이후
```python
handler = HospitalHandler(
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json"
)

result = handler.handle("강남구 동물병원?", location="강남구")

# 또는 좌표 기반
result = handler.handle(
    "근처 병원",
    latitude=37.4979,
    longitude=127.0276
)
```

---

## 🚀 점진적 마이그레이션 전략

### 방법 1: 호환성 래퍼 (권장)

기존 코드의 변경을 최소화하려면 호환성 래퍼를 만들 수 있습니다:

```python
# compatibility.py
from src.pipelines import RAGOrchestrator

class AdvancedRAGPipeline:
    """이전 API 호환성 유지"""
    
    def __init__(self, vectorstore, hospital_json_path, llm_model, score_threshold):
        self.orchestrator = RAGOrchestrator(
            vectorstore=vectorstore,
            hospital_json_path=hospital_json_path,
            llm_model=llm_model,
            score_threshold=score_threshold
        )
    
    def process_question(self, query):
        """이전 메서드명 호환성"""
        return self.orchestrator.process(query)
    
    # ... 기타 메서드들
```

사용:
```python
# 기존 코드와 동일하게 사용 가능
from compatibility import AdvancedRAGPipeline

pipeline = AdvancedRAGPipeline(vectorstore, path, model, threshold)
result = pipeline.process_question(query)
```

### 방법 2: 직접 마이그레이션

기존 코드를 새로운 구조로 직접 수정합니다:

```python
# 1. Import 변경
from src import RAGOrchestrator

# 2. 클래스명 변경
orchestrator = RAGOrchestrator(...)  # AdvancedRAGPipeline → RAGOrchestrator

# 3. 메서드명 변경
result = orchestrator.process(query)  # process_question → process
```

---

## 📋 마이그레이션 체크리스트

- [ ] 새 모듈 구조 설치
- [ ] 환경변수 설정 (.env)
- [ ] Import 문 업데이트
- [ ] 클래스명 변경
- [ ] 메서드명 변경
- [ ] 파라미터 확인
- [ ] 결과 구조 확인
- [ ] 테스트 실행
- [ ] 성능 비교
- [ ] 기존 코드 제거

---

## 🧪 테스트 및 검증

### 1단계: 호환성 테스트

```python
# test_migration.py
import json
from src import RAGOrchestrator, load_vectorstore, get_embedding_model

def test_basic_functionality():
    """기본 기능 테스트"""
    embedding_model = get_embedding_model("openai")
    vectorstore = load_vectorstore(embedding_model)
    orchestrator = RAGOrchestrator(vectorstore=vectorstore)
    
    # 의료 질문
    result1 = orchestrator.process("강아지 피부염?")
    assert result1['question_type'] == 'A'
    assert 'answer' in result1
    
    # 병원 질문
    result2 = orchestrator.process("강남역 동물병원?")
    assert result2['question_type'] == 'B'
    assert 'hospitals' in result2
    
    # 일반 질문
    result3 = orchestrator.process("반려견 훈련 팁?")
    assert result3['question_type'] == 'C'
    assert 'answer' in result3
    
    print("✓ 모든 테스트 통과")

test_basic_functionality()
```

### 2단계: 성능 비교

```python
import time

# 이전 방식
start = time.time()
for q in queries:
    result = pipeline.process_question(q)
old_time = time.time() - start

# 새로운 방식
start = time.time()
for q in queries:
    result = orchestrator.process(q)
new_time = time.time() - start

print(f"이전: {old_time:.2f}s")
print(f"새로운: {new_time:.2f}s")
print(f"성능 변화: {((new_time - old_time) / old_time * 100):+.1f}%")
```

---

## 📚 마이그레이션 후 추천 활동

1. **모듈 최적화**: 각 모듈을 세분화하여 재사용성 증대
2. **테스트 작성**: 단위 테스트와 통합 테스트 추가
3. **문서화**: 각 모듈의 사용법 문서화
4. **성능 모니터링**: 로깅 및 메트릭 추가
5. **기능 확장**: 새로운 검색기나 핸들러 추가

---

## 🆘 문제 해결

### Q: 이전 코드와 새 코드를 동시에 사용 가능한가?

**A**: 호환성 래퍼를 사용하면 가능합니다. 단계적으로 마이그레이션할 수 있습니다.

### Q: 성능이 저하되는 경우?

**A**: 다음을 확인하세요:
- 설정에서 top_k 값
- 벡터스토어 크기
- 웹 검색 활성화 여부
- LLM API 응답 시간

### Q: 기존 벡터스토어 재사용 가능한가?

**A**: 네, 완벽하게 호환됩니다. 동일한 경로에서 로드하면 됩니다.

### Q: 커스텀 핸들러를 만들려면?

**A**: `BaseHandler`를 상속하고 `handle()` 메서드를 구현하세요.

---

**마이그레이션 완료 후**: [QUICKSTART.md](./QUICKSTART.md)를 참고하여 새 기능을 활용해보세요!

