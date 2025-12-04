# 👥 기여 가이드 (Contribution Guide)

팀원들이 이 프로젝트에 기여하는 방법을 설명합니다.

## 목차

1. [역할 및 담당 영역](#역할-및-담당-영역)
2. [개발 환경 설정](#개발-환경-설정)
3. [개발 워크플로우](#개발-워크플로우)
4. [코드 스타일 가이드](#코드-스타일-가이드)
5. [테스트 작성](#테스트-작성)
6. [Pull Request 프로세스](#pull-request-프로세스)
7. [팀원별 확장 가이드](#팀원별-확장-가이드)

---

## 역할 및 담당 영역

### 🔍 데이터/검색 팀

**담당 영역**:
- `src/retriever/`: 벡터 검색 시스템
- `src/web/`: 웹 검색 시스템

**우선순위 과제**:

1. **ChromaDB 실제 연동** ⭐⭐⭐
   ```python
   # src/retriever/vector_store_retriever.py 수정
   
   def search(self, query: str, top_k: int) -> DocumentBatch:
       """ChromaDB에서 실제 검색"""
       # 현재: Mock 데이터
       # 목표: 실제 벡터 검색
       
       # 구현 예시:
       # 1. 쿼리 임베딩 생성
       # 2. ChromaDB에서 검색
       # 3. 결과 Document로 변환
   ```

2. **Google Custom Search API 연동** ⭐⭐⭐
   ```python
   # src/web/general_web_searcher.py 수정
   
   def _search_google(self, query: str) -> List[Dict]:
       """실제 Google 검색"""
       # requests로 Google API 호출
       # 결과 파싱 및 정규화
   ```

3. **Kakao Map API 연동** ⭐⭐
   ```python
   # src/web/hospital_web_searcher.py 수정
   
   def _search_kakao(self, location: str) -> List[Dict]:
       """카카오맵에서 병원 검색"""
       # 카카오맵 Places API 호출
       # 병원 정보 추출
   ```

4. **하이브리드 검색** (벡터 + BM25) ⭐⭐
   ```python
   # src/retriever/vector_store_retriever.py에 추가
   
   def search_hybrid(self, query: str, top_k: int) -> DocumentBatch:
       """벡터 검색 + 키워드 검색"""
       # 벡터 검색 결과와 BM25 결과 병합
       # 재랭킹
   ```

**체크리스트**:
- [ ] ChromaDB 로컬 환경 셋업
- [ ] 테스트 데이터 준비
- [ ] `search()` 메서드 구현
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 통과

---

### 🧠 LLM/AI 팀

**담당 영역**:
- `src/classifier/`: 의도 분류
- `src/rag/nodes/`: RAG 노드 고도화

**우선순위 과제**:

1. **LLM 기반 분류기** ⭐⭐⭐
   ```python
   # src/classifier/question_classifier.py에 추가
   
   def classify_with_llm(self, question: str) -> ClassificationResult:
       """OpenAI API를 사용한 분류"""
       from langchain.llms import ChatOpenAI
       
       llm = ChatOpenAI(model="gpt-4", temperature=0)
       
       prompt = """다음 질문을 다음 4가지 중 하나로 분류하세요:
       - medical: 반려동물 의료/건강
       - hospital: 병원 위치/정보
       - general: 일반 정보
       - unknown: 분류 불가능
       
       질문: {question}
       분류 결과:"""
       
       response = llm.invoke(prompt.format(question=question))
       # 응답 파싱하여 ClassificationResult 반환
   ```

2. **LLM 기반 답변 생성** ⭐⭐⭐
   ```python
   # src/rag/nodes/generation_node.py 수정
   
   def generation_node_llm(state: Dict[str, Any]) -> Dict[str, Any]:
       """LLM을 사용한 답변 생성"""
       from langchain.llms import ChatOpenAI
       from langchain.prompts import ChatPromptTemplate
       
       llm = ChatOpenAI(model="gpt-4", temperature=0.7)
       
       documents_text = "\n".join([
           f"- {doc.metadata.get('title', '')}: {doc.content[:200]}"
           for doc in state["documents"]
       ])
       
       prompt = ChatPromptTemplate.from_template("""
       다음은 반려동물 의료 관련 정보입니다:
       {context}
       
       질문: {query}
       
       위 정보를 바탕으로 친절하게 답변해주세요.
       """)
       
       chain = prompt | llm
       answer = chain.invoke({
           "context": documents_text,
           "query": state["query"]
       })
       
       return {"answer": answer.content}
   ```

3. **LLM 기반 관련성 평가** ⭐⭐
   ```python
   # src/rag/nodes/relevance_node.py에 추가
   
   def relevance_node_llm(state: Dict[str, Any]) -> Dict[str, Any]:
       """LLM을 사용한 정교한 관련성 판단"""
       # 각 문서에 대해 "이 문서가 질문에 답하는가?"를 LLM으로 판단
   ```

4. **프롬프트 최적화** ⭐⭐
   - Chain of Thought 적용
   - Few-shot learning 예제 추가
   - 응답 포맷 개선

**체크리스트**:
- [ ] OpenAI API 키 설정
- [ ] LLM 분류기 구현
- [ ] 테스트 케이스 작성
- [ ] 성능 평가 (정확도)
- [ ] 비용 모니터링 구현

---

### 🏥 도메인/비즈니스 팀

**담당 영역**:
- `src/mapping/`: 병원 위치 매핑
- 도메인 규칙 및 데이터

**우선순위 과제**:

1. **병원 정보 데이터베이스 구축** ⭐⭐⭐
   ```python
   # data/hospitals.json (새 파일 작성)
   {
       "hospitals": [
           {
               "id": "hospital_001",
               "name": "ABC 동물병원",
               "address": "서울시 강남구 테헤란로 123",
               "lat": 37.4979,
               "lon": 127.0276,
               "phone": "02-1234-5678",
               "services": ["일반진료", "수술", "응급"],
               "operating_hours": {...},
               "rating": 4.8,
               "reviews": 125
           }
       ]
   }
   ```

2. **병원 검색 고도화** ⭐⭐⭐
   ```python
   # src/mapping/hospital_mapper.py 수정
   
   def search_hospitals_nearby(self, coordinates, location_info):
       """실제 병원 DB에서 검색"""
       # JSON 데이터에서 읽기
       # 거리 계산
       # 정렬 및 반환
   ```

3. **의료 키워드/규칙 정의** ⭐⭐
   ```python
   # src/classifier/question_classifier.py 확장
   
   # 더 정교한 키워드 매칭
   MEDICAL_KEYWORDS.extend([
       "심장사상충", "악성림프종", "신부전", 
       "당뇨병", "갑상선", "IMHA", ...
   ])
   ```

4. **대역 데이터 수집** ⭐⭐⭐
   ```
   # data/docs/ 디렉토리에 의료 문서 추가
   - 반려견/고양이 질병 안내
   - 증상 체크리스트
   - 응급 상황 대응
   - 예방 관리
   ```

**체크리스트**:
- [ ] 주요 도시별 병원 정보 수집
- [ ] 데이터 정규화
- [ ] 의료 키워드 확장
- [ ] 의료 문서 데이터셋 구축
- [ ] 문서 벡터화

---

### 🎨 프론트엔드/UI 팀

**담당 영역**:
- `app.py`: Streamlit UI

**우선순위 과제**:

1. **UI/UX 개선** ⭐⭐⭐
   ```python
   # app.py 개선
   
   # 개선 사항:
   # 1. 질문 템플릿 추가
   # 2. 응답 시각화 개선
   # 3. 채팅 히스토리 관리
   # 4. 반응형 디자인
   ```

2. **고급 시각화** ⭐⭐
   ```python
   # 예시: 병원 위치를 지도에 표시
   import folium
   
   def show_hospitals_map(hospitals):
       m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
       for h in hospitals:
           folium.Marker(
               location=[h['lat'], h['lon']],
               popup=h['name']
           ).add_to(m)
       return m
   ```

3. **대시보드** ⭐⭐
   ```python
   # 시스템 모니터링 대시보드
   # - 쿼리 통계
   # - 응답 시간 분포
   # - 의도별 분포
   # - 사용자 만족도
   ```

4. **모바일 앱** ⭐
   ```
   # React Native / Flutter로 모바일 앱 개발
   # Streamlit API를 백엔드로 사용
   ```

**체크리스트**:
- [ ] CSS 개선
- [ ] 반응형 디자인 구현
- [ ] 지도 시각화 추가
- [ ] 대시보드 구현
- [ ] 사용성 테스트

---

## 개발 환경 설정

### 1. 저장소 클론 및 초기 설정

```bash
# 저장소 클론
git clone <repository-url>
cd pet-medical-rag

# 브랜치 확인
git branch -a

# 작업 브랜치 생성
git checkout -b feature/your-feature-name
```

### 2. 가상 환경 설정

```bash
# Python 3.10+ 확인
python --version

# 가상 환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 개발 패키지 설치
pip install pytest pytest-asyncio black flake8 mypy
```

### 3. IDE 설정

**VSCode**:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.flake8Args": ["--max-line-length=100"],
    "editor.formatOnSave": true
}
```

**PyCharm**:
- Settings → Python → Code Style → Line length: 100
- Settings → Tools → Python Integrated Tools → Default test runner: pytest

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 실제 API 키 입력
nano .env  # 또는 원하는 에디터
```

---

## 개발 워크플로우

### 1. Feature 개발

```bash
# 1. 최신 코드 동기화
git checkout main
git pull origin main

# 2. 새 브랜치 생성
git checkout -b feature/classifier-improvement

# 3. 코드 작성
# src/classifier/question_classifier.py 수정
# tests/test_classifier.py 추가

# 4. 코드 포맷팅
black src/

# 5. Linting
flake8 src/

# 6. 타입 체크
mypy src/

# 7. 테스트
pytest tests/test_classifier.py -v
```

### 2. 커밋 및 푸시

```bash
# 변경 사항 확인
git status

# 변경 사항 스테이징
git add src/classifier/question_classifier.py tests/test_classifier.py

# 의미 있는 커밋 메시지로 커밋
git commit -m "feat: Add LLM-based question classifier"

# 원격 저장소에 푸시
git push origin feature/classifier-improvement
```

### 3. Pull Request

1. GitHub에서 PR 생성
2. 다음 항목 확인:
   - [ ] 설명 작성
   - [ ] 관련 이슈 링크
   - [ ] 테스트 통과
   - [ ] 코드 리뷰 요청

---

## 코드 스타일 가이드

### Python 스타일

**PEP 8 준수**:

```python
# 좋은 예
def classify_question(
    question: str,
    intent_categories: list[str] = None,
) -> ClassificationResult:
    """
    사용자 질문을 분류합니다.
    
    Args:
        question: 분류할 질문
        intent_categories: 의도 카테고리 목록
    
    Returns:
        ClassificationResult: 분류 결과
    """
    if not question:
        raise ValueError("Question cannot be empty")
    
    # 구현
    pass


# 나쁜 예
def classify_question(question, categories=None):
    # 구현
    pass
```

### 네이밍 컨벤션

```python
# 클래스: PascalCase
class QuestionClassifier:
    pass

# 함수/메서드: snake_case
def classify_question(question: str) -> str:
    pass

# 상수: UPPER_CASE
DEFAULT_TOP_K = 5
MAX_RETRIES = 3

# 비공개 메서드: _snake_case
def _extract_keywords(text: str) -> list[str]:
    pass
```

### 타입 힌트

```python
from typing import Optional, List, Dict, Any

def search(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
) -> List[Document]:
    """문서를 검색합니다."""
    pass
```

### Docstring

```python
def invoke(
    self,
    query: str,
    intent: str = "medical",
) -> RAGResponse:
    """
    파이프라인을 실행합니다.
    
    이것은 전체 RAG 워크플로우의 진입점입니다.
    의도에 따라 적절한 처리 경로를 선택합니다.
    
    Args:
        query: 사용자 질문
        intent: 질문의 의도
            - "medical": 의료 관련
            - "hospital": 병원 정보
            - "general": 일반 정보
    
    Returns:
        RAGResponse: 생성된 응답 객체
        
    Raises:
        ValueError: 빈 query가 전달된 경우
        TimeoutError: 타임아웃 발생 시
    
    Examples:
        >>> pipeline = LangGraphRAGPipeline()
        >>> response = pipeline.invoke("반려견 피부염")
        >>> print(response.answer)
    
    Note:
        현재는 Mock 데이터를 사용합니다.
        향후 실제 LLM 호출로 대체될 예정입니다.
    """
    pass
```

---

## 테스트 작성

### Unit Test 예제

```python
# tests/test_classifier.py

import pytest
from src.classifier.question_classifier import QuestionClassifier


@pytest.fixture
def classifier():
    return QuestionClassifier()


class TestClassifyQuestion:
    """QuestionClassifier.classify() 테스트"""
    
    def test_classify_medical_question(self, classifier):
        """의료 질문 분류 테스트"""
        result = classifier.classify("반려견 피부염이 있어요")
        assert result.intent == "medical"
        assert result.confidence > 0.7
    
    def test_classify_hospital_question(self, classifier):
        """병원 질문 분류 테스트"""
        result = classifier.classify("강남역 근처 동물병원")
        assert result.intent == "hospital"
    
    def test_classify_general_question(self, classifier):
        """일반 질문 분류 테스트"""
        result = classifier.classify("반려견 예방접종은 언제")
        assert result.intent in ["medical", "general"]
    
    def test_empty_question(self, classifier):
        """빈 질문 처리"""
        result = classifier.classify("")
        assert result.intent == "unknown"
    
    def test_confidence_score(self, classifier):
        """신뢰도 점수 검증"""
        result = classifier.classify("우리 강아지가 피부염이고 병원 찾아줄래")
        assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.parametrize("query,expected_intent", [
        ("피부염 증상", "medical"),
        ("병원 위치", "hospital"),
        ("뭐해?", "general"),
    ])
    def test_various_questions(self, classifier, query, expected_intent):
        """다양한 질문 테스트"""
        result = classifier.classify(query)
        assert result.intent == expected_intent
```

### Integration Test 예제

```python
# tests/test_integration.py

def test_end_to_end_medical_query():
    """의료 질문 전체 처리 테스트"""
    from src.orchestrator.query_orchestrator import QueryOrchestrator
    
    orchestrator = QueryOrchestrator()
    result = orchestrator.process("반려견 피부염 치료법")
    
    assert result["type"] == "rag"
    assert result["data"].intent == "medical"
    assert len(result["data"].answer) > 0


def test_end_to_end_hospital_query():
    """병원 질문 전체 처리 테스트"""
    from src.orchestrator.query_orchestrator import QueryOrchestrator
    
    orchestrator = QueryOrchestrator()
    result = orchestrator.process("강남역 동물병원")
    
    assert result["type"] == "hospital"
    assert len(result["data"].hospitals) > 0
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 파일만 테스트
pytest tests/test_classifier.py -v

# 특정 테스트만 실행
pytest tests/test_classifier.py::TestClassifyQuestion::test_classify_medical_question -v

# 커버리지 리포트
pytest tests/ --cov=src --cov-report=html
```

---

## Pull Request 프로세스

### PR 작성 체크리스트

```markdown
## 설명
이 PR은 다음을 해결합니다:
- [ ] 새 기능 추가
- [ ] 버그 수정
- [ ] 성능 개선

## 변경 사항
- 점 1
- 점 2
- 점 3

## 관련 이슈
Closes #123

## 테스트
- [ ] 단위 테스트 작성함
- [ ] 통합 테스트 작성함
- [ ] 모든 테스트 통과

## 코드 품질
- [ ] Black으로 포맷팅함
- [ ] Flake8 체크 통과
- [ ] Type hints 추가함
- [ ] Docstring 작성함

## 스크린샷 (UI 변경 시)
[스크린샷 추가]
```

### 코드 리뷰 기준

**승인 전 확인 사항**:
1. ✅ 기능이 요구사항을 만족하는가?
2. ✅ 코드 스타일이 일관된가?
3. ✅ 테스트가 충분한가?
4. ✅ 문서가 업데이트되었는가?
5. ✅ 성능에 영향을 주는가?

---

## 팀원별 확장 가이드

### 데이터 팀 - 단계별 구현 계획

**Week 1: 준비**
```bash
# 1. 로컬 ChromaDB 설정
pip install chromadb

# 2. 테스트 데이터 준비
python
>>> import chromadb
>>> client = chromadb.Client()
>>> collection = client.create_collection("test")

# 3. 임베딩 함수 테스트
>>> from sentence_transformers import SentenceTransformer
>>> model = SentenceTransformer('all-MiniLM-L6-v2')
>>> embedding = model.encode("반려견 피부염")
```

**Week 2: 구현**
```python
# src/retriever/vector_store_retriever.py 수정

def search(self, query: str, top_k: int):
    # 1. 쿼리 임베딩
    embedding = self._get_embedding(query)
    
    # 2. ChromaDB 검색
    results = self.collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    
    # 3. 결과 변환
    documents = [Document(...) for ... in results]
    return DocumentBatch(documents=documents)
```

**Week 3: 테스트 및 최적화**
```bash
pytest tests/test_retriever.py -v
# 성능 테스트
time python -c "retriever.search('테스트')"
```

### LLM 팀 - 단계별 구현 계획

**Week 1: LLM 연동**
```python
from langchain.llms import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    api_key=settings.OPENAI_API_KEY
)

response = llm.invoke("테스트 질문")
```

**Week 2: 분류기 구현**
```python
# src/classifier/question_classifier.py에 추가

def classify_with_llm(self, question: str):
    prompt = "다음을 분류하세요: medical/hospital/general..."
    response = llm.invoke(prompt + question)
    # 응답 파싱
```

**Week 3: 답변 생성 개선**
```python
# src/rag/nodes/generation_node_llm 구현
# Chain of Thought 적용
```

---

**질문이나 도움이 필요하면 팀 리더에게 연락하세요!** 🙋‍♂️

**[README.md로 돌아가기](README.md)**

