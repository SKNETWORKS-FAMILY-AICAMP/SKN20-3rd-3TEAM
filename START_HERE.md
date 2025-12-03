# 🚀 시작하기 (START HERE)

## 👋 환영합니다!

반려동물 전문 **지능형 QA 및 병원 안내 고급 RAG 시스템**에 오신 것을 환영합니다! 🐾

---

## ⚡ 5분 안에 시작하기

### Step 1: 환경 설정 (2분)

```bash
# 라이브러리 설치
pip install -r requirements.txt

# .env 파일 생성
echo "OPENAI_API_KEY=sk-your-api-key" > .env
```

### Step 2: 시스템 실행 (1분)

```bash
python advanced_main.py
```

### Step 3: 메뉴 선택 (2분)

```
🐾 반려동물 전문 QA 및 병원 안내 어시스턴트

메뉴:
  1. 예시 질문 실행 (데모 + 벡터스토어 생성)
  2. 대화형 모드 (실제 사용)
  3. 배치 처리 (파일 기반)
  4. 종료

선택 (1-4): 2
```

### Step 4: 질문 입력

```
💬 질문: 개의 피부염 증상은 무엇인가요?
```

### Step 5: 답변 받기

```
📝 답변:
개의 피부염의 주요 증상은...

─────────────────────────────────────
📊 근거 정보:
  • 근거 점수: 85%
  • 내부 문서: 5개
  
📚 주요 출처:
  1. disease_data_001.json (85% 관련성)
```

---

## 🎯 무엇을 할 수 있나요?

### 의료 질문 ⚕️
```
💬 개의 피부염 증상은?
💬 고양이가 자꾸 구토해요.
💬 벼룩 예방 방법은?
```

→ ✅ 신뢰할 수 있는 의료 정보 + 출처 표시

### 병원 정보 🏥
```
💬 강남구 동물병원을 찾아주세요.
💬 24시간 응급진료 병원은?
💬 서울시 동물병원 통계
```

→ ✅ 병원 목록 + 주소, 전화 + 통계

### 일반 질문 💬
```
💬 반려동물 첫 구매 준비물?
💬 개와 고양이를 함께 키우려면?
💬 반려동물 스트레스 관리법?
```

→ ✅ 전문가 수준의 조언

---

## 📚 문서 가이드

각 상황에 맞는 문서를 선택하세요:

### 🎯 **지금 당장 사용하고 싶어요**
→ 본 문서 (START_HERE.md) 읽기
→ `python advanced_main.py` 실행

### 📖 **전체 시스템을 이해하고 싶어요**
→ **SYSTEM_SUMMARY.md** 읽기
- 시스템 개요
- 핵심 기능
- 성능 지표

### 🏗️ **기술적 아키텍처가 궁금해요**
→ **SYSTEM_ARCHITECTURE.md** 읽기
- 전체 플로우
- 각 단계 상세
- 데이터 구조

### 🎓 **Python 코드로 직접 사용하고 싶어요**
→ **USAGE_GUIDE.md** 읽기
- Python API 예시
- 배치 처리
- 디버깅 팁

### 📖 **모든 API와 기능을 알고 싶어요**
→ **ADVANCED_RAG_README.md** 읽기
- 완전한 API 문서
- 상세한 설명
- 결과 예시

### ✨ **구현 상세를 알고 싶어요**
→ **IMPLEMENTATION_SUMMARY.md** 읽기
- 생성된 파일 목록
- 코드 구조
- 구현 체크리스트

---

## 🔍 빠른 참조

### 질문 분류 방식

| 질문 | 분류 | 처리 방식 |
|------|------|---------|
| "개의 피부염?" | Type A | 내부 검색 → 근거 평가 → 웹 폴백 |
| "강남구 병원?" | Type B | CSV 조회 → 위치 필터링 |
| "양육법?" | Type C | LLM 직접 답변 |

### 신뢰도 해석

```
근거 점수 ≥ 0.6
├─ ✅ 내부 데이터로 충분
└─ 웹 검색 미수행

근거 점수 < 0.6
├─ ⚠️ 내부 데이터 부족
└─ 웹 검색 추가 수행
```

### 응답 시간

```
Type A (의료):    5-10초
Type B (병원):    1-2초
Type C (일반):    2-5초
```

---

## ⚙️ 시스템 요구사항

### 필수
- Python 3.10+
- OpenAI API 키 (필수)
- Tavily API 키 (선택 - 웹 검색용)

### 권장
- 4GB+ RAM
- 1GB+ 디스크 공간 (벡터 DB용)
- 인터넷 연결 (LLM API 호출)

---

## 🐛 문제 해결

### Q: API 키 없다는 오류
```bash
# .env 파일 확인
cat .env

# 또는 직접 설정
export OPENAI_API_KEY=sk-...
```

### Q: 벡터스토어 없다는 오류
```bash
python advanced_main.py
# 메뉴에서 1번 선택 (자동 생성)
```

### Q: 느린 응답
```
첫 실행: 정상 (벡터 임베딩 생성 중)
이후: 빠름
```

### Q: 부정확한 답변
```python
# 임계값 조정 (기본값: 0.6)
from src.medical_qa_handler import MedicalQAHandler
handler = MedicalQAHandler(vectorstore, score_threshold=0.5)
```

더 자세한 내용은 **USAGE_GUIDE.md**를 참조하세요.

---

## 💡 사용 시나리오

### 시나리오 1: 개의 증상을 알고 싶어요

```
1. python advanced_main.py
2. 메뉴: 2 (대화형 모드)
3. 질문: "개가 자꾸 구토를 해요"
4. 결과: 원인, 증상, 대처법 → 수의사 상담 권유
```

### 시나리오 2: 근처 병원을 찾고 싶어요

```
1. python advanced_main.py
2. 메뉴: 2 (대화형 모드)
3. 질문: "강남구 동물병원"
4. 결과: 87개 병원 → 주소, 전화, 상태 표시
```

### 시나리오 3: 반려동물 양육 정보가 필요해요

```
1. python advanced_main.py
2. 메뉴: 2 (대화형 모드)
3. 질문: "첫 반려동물 준비 항목?"
4. 결과: 물품 리스트, 준비사항, 비용
```

### 시나리오 4: 여러 질문을 한 번에 처리

```
1. queries.txt 파일에 질문 작성 (줄 단위)
2. python advanced_main.py
3. 메뉴: 3 (배치 처리)
4. 결과: batch_results.json에 저장
```

---

## 📊 시스템 특징

### ✨ 지능형
- 자동 질문 분류
- 최적의 처리 방식 적용

### 🔍 신뢰할 수 있는
- 근거 점수 표시
- 출처 명시
- 신뢰도 명시

### 🔄 안정적인
- 내부 데이터 우선
- 부족시 자동 웹 검색
- 오류 처리 완비

### 📈 확장 가능한
- 새로운 질문 유형 추가 용이
- 데이터 확장 가능
- 모듈식 구조

---

## 🎓 고급 사용법

### Python 코드에서 직접 사용

```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline
from src.embeddings import get_embedding_model, load_vectorstore

# 벡터스토어 로드
embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(embedding_model)

# 파이프라인 초기화
pipeline = AdvancedRAGPipeline(vectorstore)

# 질문 처리
result = pipeline.process_question("개의 피부염?")
print(result['formatted_answer'])
```

### 배치 처리

```python
questions = [
    "개의 피부염?",
    "강남구 병원",
    "양육법"
]

results = pipeline.batch_process_questions(questions)
pipeline.save_results(results, "results.json")
```

더 자세한 코드 예시는 **USAGE_GUIDE.md**를 참조하세요.

---

## ✅ 다음 단계

### 지금 바로
- [ ] `python advanced_main.py` 실행
- [ ] 메뉴에서 선택 (1 또는 2)
- [ ] 질문 입력해보기

### 나중에
- [ ] SYSTEM_SUMMARY.md 읽기
- [ ] 테스트 실행 (`python test_advanced_rag.py`)
- [ ] Python API 익히기 (USAGE_GUIDE.md)

### 개발자라면
- [ ] SYSTEM_ARCHITECTURE.md 학습
- [ ] ADVANCED_RAG_README.md 정독
- [ ] 코드 커스터마이징

---

## 🎁 제공되는 것

✅ **완전한 코드** - 즉시 사용 가능한 Python 패키지
✅ **풍부한 문서** - 6개의 상세 문서
✅ **테스트 코드** - 모든 기능 테스트 가능
✅ **샘플 데이터** - 19개의 예제 질문

---

## 📞 문제 해결 및 지원

### 일반 질문
→ USAGE_GUIDE.md의 FAQ 섹션 참조

### 기술 문제
→ USAGE_GUIDE.md의 "트러블슈팅" 섹션 참조

### 아키텍처 이해
→ SYSTEM_ARCHITECTURE.md 참조

### API 사용법
→ ADVANCED_RAG_README.md 참조

---

## 🏆 성공적인 사용을 위한 팁

1. **첫 실행은 시간이 걸려요**
   - Chroma 벡터스토어 생성 중 (정상)
   - 메뉴 1번 선택하면 자동 생성

2. **API 키를 확인하세요**
   - OpenAI API 키 필수
   - Tavily 키는 선택 (웹 검색용)

3. **의료 정보는 참고만 하세요**
   - 실제 진단/치료는 수의사 상담 필수
   - 응급시 즉시 동물병원 방문

4. **병원 정보는 최신 정보인지 확인하세요**
   - 정기적 업데이트 필요
   - 직접 연락해서 확인 권장

---

## 🎯 최종 체크리스트

시스템 사용 전 확인사항:

- [ ] Python 3.10+ 설치 완료
- [ ] `pip install -r requirements.txt` 실행 완료
- [ ] `.env` 파일에 API 키 설정 완료
- [ ] `data/raw` 디렉토리 확인 완료
- [ ] `python advanced_main.py` 실행 확인 완료

모든 항목이 완료되었다면, 이제 **시스템을 사용할 준비가 되었습니다!** 🚀

---

## 🎉 준비됐나요?

**이제 시작하세요:**

```bash
python advanced_main.py
```

**또는 코드로 직접 사용:**

```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline
# 위 가이드의 "고급 사용법" 참조
```

---

## 📚 전체 문서 맵

```
START_HERE.md (본 문서)
├─ 빠르게 시작하고 싶어요
│  └─ "5분 안에 시작하기" 참조
│
├─ 시스템을 이해하고 싶어요
│  ├─ SYSTEM_SUMMARY.md
│  └─ SYSTEM_ARCHITECTURE.md
│
├─ 사용 방법을 알고 싶어요
│  ├─ USAGE_GUIDE.md
│  └─ ADVANCED_RAG_README.md
│
└─ 구현을 배우고 싶어요
   └─ IMPLEMENTATION_SUMMARY.md
```

---

## 🐾 마지막 말씀

이 시스템은 반려동물을 사랑하는 모든 사람을 위해 만들어졌습니다.

**신뢰할 수 있는 의료 정보, 효율적인 병원 검색, 일반적인 양육 조언**을 한 곳에서 얻을 수 있습니다.

반려동물의 건강과 행복을 위해 이 시스템을 잘 활용해주세요! 🐾

---

**🚀 지금 시작하세요!**

```bash
python advanced_main.py
```

---

**질문이나 도움이 필요하신가요?**

→ USAGE_GUIDE.md의 FAQ 섹션 확인
→ SYSTEM_ARCHITECTURE.md로 기술 상세 학습
→ ADVANCED_RAG_README.md로 API 이해

---

**행운을 빕니다! 🍀**

---

**버전**: 2.0 (Advanced RAG)
**상태**: ✅ Production Ready
**마지막 업데이트**: 2025년 12월 3일

