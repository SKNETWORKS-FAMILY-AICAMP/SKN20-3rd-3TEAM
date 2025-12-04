# 🚀 빠른 시작 가이드 (Quick Start)

## 5분 안에 시작하기

### 1단계: 설치 (1분)

```bash
# Python 3.10+ 확인
python --version

# 패키지 설치
pip install -r requirements.txt

# 또는 개발 모드로 설치
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정 (2분)

```bash
# .env 파일 복사
cp .env.example .env

# 에디터에서 .env 열기
# OPENAI_API_KEY 등 필요한 값 입력 (현재는 placeholder 가능)
```

### 3단계: 실행 (2분)

```bash
# Streamlit 앱 시작
streamlit run app.py

# 브라우저에서 http://localhost:8501 열기
```

---

## 기본 사용 방법

### Python 코드에서 사용

```python
from src.orchestrator.query_orchestrator import QueryOrchestrator

# 오케스트레이터 초기화
orchestrator = QueryOrchestrator()

# 질문 처리
result = orchestrator.process("우리 강아지가 피부염이 있는데 어떻게 하죠?")

# 결과 확인
print(result["type"])        # "rag"
print(result["data"].answer)  # 생성된 답변
```

### 분류기만 사용

```python
from src.classifier.question_classifier import QuestionClassifier

classifier = QuestionClassifier()

# 질문 분류
result = classifier.classify("강남역 근처 동물병원")
print(result.intent)         # "hospital"
print(result.confidence)     # 0.95
```

### 벡터 검색 사용

```python
from src.retriever.vector_store_retriever import VectorStoreRetriever

retriever = VectorStoreRetriever()

# 검색
results = retriever.search("반려견 피부염 증상")
for doc in results.documents:
    print(f"{doc.id}: {doc.content[:100]}...")
```

### RAG 파이프라인 사용

```python
from src.rag.langgraph_crag_pipeline import LangGraphRAGPipeline

pipeline = LangGraphRAGPipeline()

# 파이프라인 실행
response = pipeline.invoke("반려견 피부염 치료법", intent="medical")
print(response.answer)
```

---

## 프로젝트 구조 한눈에 보기

```
pet_medical_rag/
├── app.py                    # Streamlit UI
├── requirements.txt          # 패키지 의존성
│
├── src/
│   ├── classifier/           # 의도 분류
│   ├── retriever/            # 벡터 검색
│   ├── web/                  # 웹 검색
│   ├── mapping/              # 병원 매핑
│   ├── rag/                  # CRAG 파이프라인
│   ├── orchestrator/         # 시스템 조율
│   ├── config/               # 설정
│   ├── types/                # 타입 정의
│   └── utils/                # 헬퍼 함수
│
├── tests/                    # 테스트
├── data/                     # 데이터
├── README.md                 # 상세 가이드
├── ARCHITECTURE.md           # 아키텍처 설명
├── CONTRIBUTION.md           # 팀원 확장 가이드
└── QUICK_START.md            # 이 파일
```

---

## 핵심 클래스

| 클래스 | 역할 | 위치 |
|--------|------|------|
| `QuestionClassifier` | 질문 분류 | `src/classifier/` |
| `VectorStoreRetriever` | 벡터 검색 | `src/retriever/` |
| `HospitalWebSearcher` | 병원 검색 | `src/web/` |
| `GeneralWebSearcher` | 일반 검색 | `src/web/` |
| `HospitalMapper` | 위치 매핑 | `src/mapping/` |
| `LangGraphRAGPipeline` | RAG 파이프라인 | `src/rag/` |
| `QueryOrchestrator` | 전체 조율 | `src/orchestrator/` |

---

## 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 모듈만 테스트
pytest tests/test_classifier.py -v

# 커버리지 확인
pytest tests/ --cov=src
```

---

## 문제 해결

### 패키지 설치 실패

```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 초기화 후 재설치
pip install --no-cache-dir -r requirements.txt
```

### API 키 오류

```bash
# .env 파일 확인
cat .env

# 또는 환경 변수 직접 설정
export OPENAI_API_KEY="your-key-here"
```

### Streamlit 포트 충돌

```bash
# 다른 포트에서 실행
streamlit run app.py --server.port 8502
```

---

## 다음 단계

1. **[README.md](README.md)** - 전체 가이드 읽기
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 시스템 아키텍처 이해
3. **[CONTRIBUTION.md](CONTRIBUTION.md)** - 기여 방법 배우기
4. **팀별 역할** - 자신의 담당 영역에서 기여 시작

---

## 자주 묻는 질문 (FAQ)

**Q: Mock 데이터가 실제 데이터로 바뀌나요?**
- A: 네! 각 모듈의 TODO 주석을 따라 실제 API 연동하면 됩니다.

**Q: LLM을 어떻게 추가하나요?**
- A: `src/classifier/question_classifier.py`와 `src/rag/nodes/generation_node.py` 파일의 `_with_llm` 메서드를 구현하면 됩니다.

**Q: 데이터를 어디에 저장하나요?**
- A: 벡터DB는 `data/chroma_db/`, 의료 문서는 `data/docs/`에 저장됩니다.

**Q: 팀과 함께 어떻게 개발하나요?**
- A: [CONTRIBUTION.md](CONTRIBUTION.md)의 "개발 워크플로우" 섹션을 참조하세요.

---

## 유용한 명령어

```bash
# 모든 import 정렬 및 포맷팅
black src/ tests/

# 코드 품질 확인
flake8 src/

# 타입 체크
mypy src/

# 로그 레벨 변경하여 실행
LOG_LEVEL=DEBUG streamlit run app.py

# 특정 테스트만 실행
pytest tests/test_classifier.py::TestClassifyQuestion::test_classify_medical_question -v
```

---

## 성능 최적화 팁

1. **첫 실행이 느린 경우**
   - ChromaDB 초기화 대기 (몇 초 소요)

2. **메모리 부족**
   - 배치 크기 줄이기 (`.env`에서 조정)

3. **API 호출 제한**
   - 결과 캐싱 활용

---

**더 자세한 정보는 [README.md](README.md)를 참조하세요!** 📚

**행운을 빕니다! 🐾**

