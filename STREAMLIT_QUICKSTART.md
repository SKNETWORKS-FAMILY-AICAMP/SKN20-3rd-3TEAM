# 🚀 Streamlit 앱 빠른 시작 가이드

## 📋 개요

공통 모듈을 사용한 **기본 Streamlit RAG 웹 앱**입니다.

```
앱: app.py
크기: 약 400줄
대상: 기본 사용자
```

---

## ⚡ 5초 시작

### Step 1: 필수 패키지 설치
```bash
pip install streamlit
```

### Step 2: 환경 변수 설정
```bash
# .env 파일 또는 환경 변수
export OPENAI_API_KEY="sk-..."
```

### Step 3: 실행
```bash
streamlit run app.py
```

### Step 4: 웹 브라우저 열림
자동으로 `http://localhost:8501` 열림

---

## 🎨 UI 구성

```
┌─────────────────────────────────────────────────────┐
│               🏥 의료 RAG 챗봇                       │
│          공통 모듈 기반 RAG 시스템                    │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  ⚙️ 설정     │         💬 대화                      │
│              │                                      │
│ 📊 상태      │  [이전 대화 기록]                    │
│              │                                      │
│ 👁️ 옵션      │  [AI 답변]                          │
│              │  📚 참고 문서                         │
│ 💬 관리      │  🐛 디버그 정보                      │
│              │                                      │
│ 📈 통계      │  ─────────────────────────           │
│              │  📝 질문 입력                        │
│ ❓ 도움말     │  [입력창]      [📤 제출]            │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

---

## 🎯 주요 기능

### 1️⃣ 채팅 인터페이스
- 사용자 질문 입력
- AI 답변 표시
- 실시간 처리

### 2️⃣ 출처 표시
- 참고한 문서 목록
- 유사도 점수
- 접기/펼치기 가능

### 3️⃣ 응답 시간 표시
- 각 답변의 처리 시간
- 성능 모니터링

### 4️⃣ 디버그 정보
- 검색된 문서 수
- 관련성 점수
- 웹 검색 여부

### 5️⃣ 대화 통계
- 총 질문 수
- 성공률
- 평균 응답 시간

### 6️⃣ 설정 옵션
- 출처 표시 on/off
- 디버그 정보 on/off
- 대화 초기화

---

## 💻 사용 예시

### 기본 사용 흐름

```
1️⃣ 앱 실행
   streamlit run app.py

2️⃣ 초기화 대기
   🔄 RAG 시스템 초기화 중...
   📚 임베딩 모델 로드 중...
   💾 벡터 저장소 로드 중...
   🔍 검색기 초기화 중...
   🤖 LLM 클라이언트 초기화 중...
   ✅ RAG 시스템 준비 완료!

3️⃣ 질문 입력
   입력: "강아지 피부 질환의 증상은?"

4️⃣ 답변 생성
   🔄 답변을 생성 중입니다...
   (2-3초 대기)

5️⃣ 결과 표시
   🤖 AI Assistant
   "강아지 피부 질환은 다양한 원인으로..."
   ⏱️ 2.34s
   
   📚 참고한 문서 (3개)
   [1] 강아지 피부 질환 - 유사도: 89%
   [2] 피부염 증상 - 유사도: 82%
   [3] 질병 진단 - 유사도: 75%
```

---

## 📚 화면 설명

### 메인 영역

**대화 기록 표시**
```
👤 You
강아지 피부 질환의 증상은?

🤖 AI Assistant
강아지 피부 질환은 가려움증, 탈모, 피부 발적 등의 증상을 보입니다...
⏱️ 2.34s

📚 참고한 문서 (3개)
[1] 강아지 피부 질환...
```

### 사이드바

**📊 시스템 상태**
- ✅ RAG 시스템 준비됨

**👁️ 표시 옵션**
- ☑️ 출처 표시
- ☐ 디버그 정보 표시

**💬 대화 관리**
- 🔄 새로고침 버튼
- 🗑️ 초기화 버튼

**📈 대화 통계**
```
┌─────┐ ┌────┐ ┌──────┐
│  5  │ │100%│ │2.34s │
│총질문│ │성공률│ │평균시간│
└─────┘ └────┘ └──────┘
```

---

## 🔧 문제 해결

### Q1: "❌ 초기화 실패" 에러
**원인**: 벡터 저장소 경로 문제
```bash
# 해결:
mkdir -p ./chroma_db
```

### Q2: "OPENAI_API_KEY가 설정되지 않았습니다"
**원인**: API 키 미설정
```bash
# 해결:
export OPENAI_API_KEY="sk-..."
```

### Q3: 질문 입력 후 오류 발생
**원인**: 벡터 저장소에 문서 없음
```python
# 해결: 문서 추가 필요
# common/extensions/vectorstores 참고
```

### Q4: 응답이 너무 느림
**원인**: 첫 실행 (캐싱 미작동)
```
해결: 다시 질문하면 빨라집니다
```

---

## ⚙️ 커스터마이징

### 앱 제목 변경
```python
# app.py의 st.set_page_config()
page_title="내 앱 이름",
page_icon="🎯",  # 원하는 이모지
```

### Top-K 값 변경
```python
# process_question() 함수
response = st.session_state.pipeline.process(
    question,
    top_k=10,  # 5에서 10으로 변경
)
```

### 모델 변경
```python
# initialize_pipeline() 함수
embedding = OpenAIEmbeddingModel(
    model_name="text-embedding-3-large"  # small → large
)

llm_client = OpenAILLMClient(
    model_name="gpt-4",  # gpt-4o-mini → gpt-4
    temperature=0.5,  # 0.7 → 0.5
)
```

### 컬렉션 이름 변경
```python
# initialize_pipeline() 함수
vectorstore = ChromaVectorStore(
    embedding_model=embedding,
    persist_directory="./chroma_db",
    collection_name="my_documents"  # 변경
)
```

---

## 📱 다양한 사용 시나리오

### 시나리오 1: 의료 상담
```
입력: "강아지가 계속 긁어요"
출력: [의료 정보] + [출처]
```

### 시나리오 2: 제품 정보
```
입력: "이 제품의 부작용은?"
출력: [제품 정보] + [출처]
```

### 시나리오 3: FAQ
```
입력: "자주 묻는 질문?"
출력: [FAQ 답변] + [출처]
```

---

## 🚀 배포 옵션

### 1. 로컬 실행 (현재)
```bash
streamlit run app.py
```

### 2. Streamlit Cloud 배포
```bash
# 1. GitHub에 push
git push origin main

# 2. Streamlit Cloud에서 배포
# https://streamlit.io/cloud
```

### 3. Docker 배포
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t rag-app .
docker run -p 8501:8501 rag-app
```

---

## 📊 성능 특성

| 항목 | 수치 |
|------|------|
| 첫 실행 시간 | 5-6초 (초기화) |
| 이후 질문 응답 | 2-4초 |
| 메모리 사용 | ~3-5GB |
| 동시 사용자 | 1명 (기본) |

---

## 💡 팁

### 1. 빠른 응답을 위해
- 구체적이고 짧은 질문 입력
- Top-K를 5에서 3으로 줄이기

### 2. 더 정확한 답변을 위해
- 상세한 설명과 함께 질문
- 출처 정보 확인

### 3. 대화 초기화할 때
- 사이드바의 "🗑️ 초기화" 버튼
- 또는 터미널에서 Ctrl+C 후 재실행

---

## 🎓 다음 단계

### 1. 기본 앱 이해
- [app.py](./app.py) 코드 분석

### 2. 고급 앱으로 확장
- 설정 프리셋 추가
- 성능 그래프 추가
- 모델 선택 기능 추가

### 3. 공통 모듈 학습
- [COMMON_MODULE_GUIDE.md](./common/COMMON_MODULE_GUIDE.md) 참고
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) 참고

---

## 📞 지원

### 문제 발생 시
1. [문제 해결](#-문제-해결) 섹션 확인
2. [common/README.md](./common/README.md) 참고
3. 프로젝트 리드에 연락

### 더 알고 싶을 때
- 📖 [README.md](./README.md)
- 📚 [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- 🏗️ [common/STRUCTURE.md](./common/STRUCTURE.md)

---

## ✨ 주요 기능 요약

✅ **채팅 UI**: 사용자 친화적 인터페이스
✅ **출처 표시**: 답변의 신뢰성 확보
✅ **성능 모니터링**: 응답 시간 추적
✅ **디버그 정보**: 개발자 디버깅 기능
✅ **대화 통계**: 사용량 추적
✅ **설정 옵션**: 유연한 커스터마이징

---

## 🎉 완성!

**Streamlit 기본 앱이 준비되었습니다!** 🚀

```bash
streamlit run app.py
```

로 지금 바로 시작하세요! 🎯


