# 🏥 RAG 시스템 프로젝트 (Streamlit 웹 애플리케이션)

의료 데이터를 기반으로 한 **LangGraph CRAG (Corrective RAG) 시스템**입니다.  
**Streamlit 웹 기반 인터페이스**로 쉽고 편리하게 사용할 수 있습니다.

## 🚀 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. API 키 설정
# .env 파일 생성 후 OPENAI_API_KEY 추가

# 3. 앱 실행 (기본 버전)
streamlit run app.py

# 또는 고급 버전 실행
streamlit run app_advanced.py
```

👉 [빠른 시작 가이드](./QUICKSTART.md)를 참조하세요!

## 📁 프로젝트 구조

```
.
├── app.py                          # ⭐ Streamlit 메인 웹 앱
├── app_advanced.py                 # 🚀 고급 기능 웹 앱
├── streamlit_config.py             # ⚙️ 설정 관리
├── .streamlit/
│   └── config.toml                 # Streamlit 설정
├── QUICKSTART.md                   # 🚀 5분 시작 가이드
├── STREAMLIT_GUIDE.md              # 📖 상세 사용 설명서
├── src/
│   ├── pipeline.py                 # LangGraph CRAG 파이프라인
│   ├── retrieval.py                # Retriever (Top-K=5)
│   ├── embeddings.py               # Embedding 모델 관리
│   ├── ingestion.py                # 데이터 로딩
│   ├── chunking.py                 # 문서 분할
│   └── ...
├── chroma_db/                      # 벡터 DB (사전 생성됨)
├── requirements.txt                # 필수 패키지 목록
└── README.md                       # 이 파일
```

## ✨ 주요 기능

### 🎯 핵심 RAG 기능
- **Retrieval**: 벡터 DB에서 Top-K=5 문서 검색 (Similarity Score)
- **Grading**: LLM 기반 문서 관련성 평가 (Yes/No)
- **Web Search Fallback**: 관련 문서 부족 시 Tavily API로 자동 웹 검색
- **Generation**: 컨텍스트 기반 LLM 답변 생성

### 🌐 Streamlit 웹 인터페이스
- ✅ 채팅 형식의 직관적인 UI
- 📚 참고 문서 출처 표시 (내부/웹 구분)
- 🐛 디버그 정보 보기 (Similarity Score, 관련성 판정, 웹 검색 여부)
- 📊 대화 통계 및 성능 모니터링
- 💾 세션 상태 자동 유지

### ⚙️ 고급 기능 (app_advanced.py)
- 🎚️ 설정 프리셋 (Fast, Balanced, Accurate, Creative)
- 🔧 LLM 모델 선택 (gpt-4o-mini, gpt-4-turbo, gpt-4o)
- 🎛️ Top-K, Temperature 동적 조정
- ⏱️ 성능 추적 및 그래프 시각화
- 📈 응답 시간 추이 분석

### 📱 사용자 경험
- 🚀 한 번의 설정으로 자동 캐싱 (빠른 재로딩)
- 🎨 반응형 디자인 및 커스텀 CSS
- 💡 예시 질문 빠른 선택
- 🗑️ 대화 초기화 및 재시작

## 🔧 설치 및 실행

### 1단계: 필수 패키지 설치

```bash
pip install -r requirements.txt
```

**주요 패키지:**
- streamlit: 웹 애플리케이션 프레임워크
- langchain: LLM 오케스트레이션
- langgraph: 상태 그래프 (CRAG 패턴)
- chromadb: 벡터 DB
- openai: OpenAI API

### 2단계: API 키 설정

`.env` 파일을 프로젝트 루트에 생성:

```bash
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # 선택사항 (웹 검색)
```

**API 획득:**
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com/

### 3단계: Streamlit 앱 실행

**기본 버전 (권장):**
```bash
streamlit run app.py
```

**고급 버전 (설정 프리셋 포함):**
```bash
streamlit run app_advanced.py
```

🌐 자동으로 브라우저가 열립니다 → `http://localhost:8501`

## 📖 가이드 문서

| 문서 | 설명 |
|------|------|
| [🚀 QUICKSTART.md](./QUICKSTART.md) | 5분 안에 시작하기 |
| [📖 STREAMLIT_GUIDE.md](./STREAMLIT_GUIDE.md) | 상세 사용 설명서 |
| [⚙️ streamlit_config.py](./streamlit_config.py) | 설정 및 프리셋 |

## 💻 코드에서 직접 사용

기존 터미널 환경에서도 RAG를 사용할 수 있습니다:

```python
from src.embeddings import get_embedding_model, load_vectorstore
from src.retrieval import create_retriever
from src.pipeline import LangGraphRAGPipeline

# RAG 파이프라인 설정
embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model)
retriever = create_retriever(vectorstore, top_k=5)

pipeline = LangGraphRAGPipeline(retriever, debug=True)

# 질문하기
result = pipeline.rag_pipeline_with_sources("강아지 피부 질환의 증상은?")
print(result['answer'])
print(result['sources'])
```

## ⚙️ 설정 옵션

### Streamlit 설정 프리셋

**app_advanced.py 사이드바에서 선택:**

| 프리셋 | 속도 | 품질 | 용도 |
|--------|------|------|------|
| ⚡ Fast | 1-2초 | 보통 | 빠른 답변 필요 |
| ⚖️ Balanced | 2-3초 | 좋음 | 일반적인 사용 (기본값) |
| 🎯 Accurate | 3-5초 | 최고 | 정확한 답변 필요 |
| ✨ Creative | 3-5초 | 창의적 | 다양한 관점 필요 |

### LLM 모델 선택

```python
# app.py 수정
pipeline = LangGraphRAGPipeline(
    retriever,
    llm_model="gpt-4o",  # "gpt-4o-mini", "gpt-4-turbo", "gpt-4o"
    temperature=0.0,
    debug=False
)
```

### Top-K 값 조정

```python
# retriever top-k 설정
retriever = create_retriever(vectorstore, top_k=10)
```

## 📚 코어 모듈 설명

### 🔄 pipeline.py - LangGraph CRAG 파이프라인
```
[질문] → [Retrieve] → [Grade] → [Decision] 
              ↓          ↓          ↓
          Top-K=5    Yes/No     Generate?
                               ↓
                        [Web Search] (선택)
                               ↓
                          [Generate]
                               ↓
                         [최종 답변]
```

**주요 클래스:**
- `LangGraphRAGPipeline`: 5단계 CRAG 파이프라인 구현
- `CRAGState`: 상태 관리
- `rag_pipeline_with_sources()`: 답변 + 출처 정보 반환

### 🔍 retrieval.py - 벡터 검색
- `SimpleRetriever`: Top-K 검색 (기본값: 5)
- `retrieve_with_scores()`: 유사도 점수 함께 반환
- Similarity Score: 1 - cosine_distance

### 🧠 embeddings.py - 임베딩 모델
- `get_embedding_model()`: OpenAI 또는 HuggingFace 선택
- `load_vectorstore()`: Chroma DB 로드
- 기본 모델: `text-embedding-3-small`

### 📄 ingestion.py - 데이터 로딩
- JSON 파일 로드 및 Document 변환
- 메타데이터 추출 (file_name, department, title 등)

### ✂️ chunking.py - 문서 분할
- 토큰 기반 청킹 (min: 300, max: 500)
- Overlap: 25% (중복 처리)

## 🚨 주의사항

1. **API 키**: `.env` 파일에 `OPENAI_API_KEY` 필수 설정
2. **벡터 DB**: 사전 생성된 `chroma_db` 디렉토리 필요
3. **메모리**: 임베딩 모델 로드 시 3-4GB 필요
4. **네트워크**: OpenAI API 통신 필수

## 🐛 트러블슈팅

### "OPENAI_API_KEY not found"
```bash
# .env 파일 생성 및 API 키 추가
OPENAI_API_KEY=sk-your-key-here
```

### "Chroma DB not found"
```bash
# 기존 chroma_db 디렉토리 확인
# 또는 데이터 재로드 필요
python src/ingestion.py
```

### "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### 느린 응답
```bash
# 더 빠른 모델 사용: app.py에서 llm_model 변경
llm_model="gpt-4o-mini"  # 빠름

# 또는 고급 버전에서 Fast 프리셋 선택
```

더 많은 도움말은 [STREAMLIT_GUIDE.md](./STREAMLIT_GUIDE.md) 참조

## 📊 성능 기준

| 작업 | 시간 | 
|------|------|
| 파이프라인 초기화 | 2-3초 |
| 평균 응답 시간 | 2-4초 (gpt-4o-mini) |
| 웹 검색 포함 | 4-6초 |
| 시스템 총 메모리 | 3-5GB |

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.

