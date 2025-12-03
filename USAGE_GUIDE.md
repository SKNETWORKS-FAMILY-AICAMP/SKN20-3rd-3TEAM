# 🐾 반려동물 QA 어시스턴트 사용 가이드

## 빠른 시작 (Quick Start)

### 1. 환경 설정

```bash
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=sk-...your-key-here...
TAVILY_API_KEY=tvly-...your-key-here...
EOF
```

### 2. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 3. 시스템 실행

```bash
python advanced_main.py
```

메뉴에서 선택:
- `1`: 예시 질문 실행 (데모)
- `2`: 대화형 모드 (일반 사용)
- `3`: 배치 처리 (파일 기반)
- `4`: 종료

---

## 사용 시나리오별 가이드

### 시나리오 1: 단순 의료 질문

**목표**: 개의 피부염 증상에 대해 알아보기

```
입력: "개의 피부염 증상은 무엇인가요?"

시스템 처리:
1. 질문 분류 → Type A (의료 질문)
2. 내부 Chroma 검색 → 5개 문서 검색
3. 근거 평가 → 점수: 0.85 (충분함)
4. RAG 답변 생성

출력:
- 증상 정보
- 근거 점수 (85%)
- 출처 명시
```

---

### 시나리오 2: 복합 의료 질문

**목표**: 내부 정보가 부족한 특수 질환에 대해 알아보기

```
입력: "반려동물의 드문 유전질환 치료법은?"

시스템 처리:
1. 질문 분류 → Type A (의료)
2. 내부 검색 → 결과 부족
3. 근거 평가 → 점수: 0.45 (부족)
4. 웹 검색 자동 수행
5. 통합 RAG 답변 생성

출력:
- 웹 검색 결과 포함
- 근거 점수 표시 (0.45 → 웹 검색 수행함)
- 혼합된 출처 표시
```

---

### 시나리오 3: 병원 검색

**목표**: 특정 지역의 동물병원 찾기

```
입력: "강남구 동물병원을 찾아주세요."

시스템 처리:
1. 질문 분류 → Type B (병원)
2. 정규식으로 "강남구" 추출
3. CSV에서 필터링
4. 병원 정보 정렬 및 제공

출력:
구별 병원 정보:
- 강남구: 387개 병원 (상위 10개 표시)
- 전화, 주소 포함
```

---

### 시나리오 4: 일반 질문

**목표**: 반려동물 양육 팁 얻기

```
입력: "반려동물을 처음 키우는데 뭘 준비해야 하나요?"

시스템 처리:
1. 질문 분류 → Type C (일반)
2. LLM 직접 호출
3. 답변 생성

출력:
- 준비물 목록
- 케어 팁
- 비용 정보
```

---

## Python API 직접 사용

### 기본 사용법

```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline
from src.embeddings import get_embedding_model, load_vectorstore

# 1. 벡터스토어 로드
embedding_model = get_embedding_model("openai")
vectorstore = load_vectorstore(
    embedding_model,
    persist_directory="./chroma_db",
    collection_name="rag_collection"
)

# 2. 파이프라인 초기화
pipeline = AdvancedRAGPipeline(vectorstore)

# 3. 질문 처리
result = pipeline.process_question("개의 피부염 증상은?")

# 4. 결과 접근
print(f"질문: {result['question']}")
print(f"분류: {result['classification_type']}")  # A, B, C
print(f"신뢰도: {result['classification_confidence']:.1%}")
print(f"\n답변:\n{result['formatted_answer']}")
```

### 배치 처리

```python
# 여러 질문 한 번에 처리
questions = [
    "개의 피부염 증상은?",
    "강남구 동물병원",
    "반려동물 양육법",
]

results = pipeline.batch_process_questions(questions)

# 결과 저장
pipeline.save_results(results, "my_results.json")
```

### 각 모듈 직접 사용

#### 질문 분류만 사용

```python
from src.question_classifier import QuestionClassifier

classifier = QuestionClassifier()
question_type, confidence, reason = classifier.classify("개의 피부염?")

print(f"Type: {question_type.name}")  # MEDICAL
print(f"Confidence: {confidence:.1%}")
print(f"Reason: {reason}")
```

#### 의료 질문만 처리

```python
from src.medical_qa_handler import MedicalQAHandler

handler = MedicalQAHandler(vectorstore, score_threshold=0.6)
result = handler.handle_medical_question("개의 피부염 증상?")

print(f"Relevance Score: {result['relevance_score']:.1%}")
print(f"Web Search Used: {result['used_web_search']}")
print(f"Answer: {result['answer']}")
```

#### 병원 검색만 사용

```python
from src.hospital_handler import HospitalHandler

handler = HospitalHandler()

# 지역별 검색
hospitals = handler.search_by_location("강남구")
for h in hospitals[:5]:
    print(f"{h['name']}: {h['phone']}")

# 통계
stats = handler.get_statistics()
print(f"총 병원: {stats['total_hospitals']}")
for district, count in stats['top_districts'][:5]:
    print(f"  {district}: {count}")
```

---

## 결과 해석

### Type A (의료 질문) 결과

```python
{
    'classification_type': 'MEDICAL',
    'classification_confidence': 0.92,  # 92% 확신
    'relevance_score': 0.78,            # 78% 근거 충분
    'internal_search_results': 5,       # 5개 문서 검색
    'web_search_results': 0,            # 웹 검색 미수행
    'used_web_search': False,
    'answer': '...',                    # 답변 내용
    'sources': [
        {
            'metadata': {
                'file_name': 'disease_001.json',
                'department': '피부과',
                'title': '피부염'
            },
            'relevance_score': 0.95      # 95% 관련성
        },
        ...
    ]
}
```

**해석**:
- ✅ 높은 신뢰도 (92%)
- ✅ 충분한 근거 (78% > 60% threshold)
- ✅ 내부 데이터로만 답변 가능
- ✅ 출처와 근거 명시됨

---

### Type B (병원 질문) 결과

```python
{
    'classification_type': 'HOSPITAL',
    'classification_confidence': 0.88,
    'hospitals': [
        {
            'name': '강남동물병원',
            'address': '서울 강남구 테헤란로 123',
            'phone': '02-1234-5678',
            'district': '강남구',
            'status': '정상',
            'business_type': '개인동물의료'
        },
        ...
    ],
    'statistics': {
        'total_hospitals': 5287,
        'top_districts': [
            ('강남구', 387),
            ('서초구', 342),
            ...
        ]
    },
    'response': '...'  # 포맷된 텍스트
}
```

**해석**:
- ✅ 87개 병원 검색
- ✅ 상세 정보 포함
- ✅ 통계 정보 제공

---

### Type C (일반 질문) 결과

```python
{
    'classification_type': 'GENERAL',
    'classification_confidence': 0.88,
    'answer': '...',  # LLM 답변
    'sources': [],     # 외부 검증 없음
    'used_external_search': False
}
```

**해석**:
- ℹ️ 외부 데이터 검증 없음
- ℹ️ LLM 모델의 훈련 데이터 기반

---

## 디버깅 및 문제 해결

### 문제 1: "OPENAI_API_KEY not found"

**원인**: API 키 미설정

**해결**:
```bash
# .env 파일 확인
cat .env

# 또는 직접 설정
export OPENAI_API_KEY=sk-...
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

---

### 문제 2: "Chroma database not found"

**원인**: 벡터스토어 미생성

**해결**:
```bash
# 예시 쿼리 실행 (벡터스토어 자동 생성)
python advanced_main.py  # 메뉴: 1번
```

---

### 문제 3: 느린 응답 속도

**원인**: 
- 첫 실행 (임베딩 생성 중)
- 큰 데이터셋
- 네트워크 지연

**해결**:
- 첫 실행 후에는 빠름
- 배치 처리 사용
- 캐싱 활용

---

### 문제 4: 정확하지 않은 답변

**의료 질문**:
- 내부 데이터 부족 → 웹 검색 활용
- 관련성 점수 낮음 → 임계값 조정

```python
# 임계값 조정 (기본값: 0.6)
handler = MedicalQAHandler(
    vectorstore,
    score_threshold=0.5  # 더 낮은 기준
)
```

**병원 질문**:
- 정확한 지역명 사용 (예: "강남구" not "강남")

**일반 질문**:
- 명확한 질문 작성
- 컨텍스트 제공

---

## 고급 사용법

### 1. 커스텀 필터 적용

```python
# Type B: 병원 데이터 커스텀 필터
from src.hospital_handler import HospitalHandler

handler = HospitalHandler()

# 특정 상태의 병원만 검색
all_hospitals = handler.search_by_location("강남구")
active_hospitals = [h for h in all_hospitals 
                    if h['status'] == '정상']

print(f"활성 병원: {len(active_hospitals)}개")
```

### 2. 점수 기반 결과 정렬

```python
# Type A: 관련성 높은 순으로 정렬
result = pipeline.process_question("개 피부염?")

sorted_sources = sorted(
    result['sources'],
    key=lambda x: x['relevance_score'],
    reverse=True
)

print("관련성 순서:")
for i, source in enumerate(sorted_sources, 1):
    score = source['relevance_score']
    print(f"{i}. ({score:.0%}) {source['metadata']['title']}")
```

### 3. 신뢰도 기반 응답 처리

```python
result = pipeline.process_question("개 피부염?")

if result['classification_confidence'] >= 0.9:
    print("✅ 높은 신뢰도 분류")
    process_with_high_priority(result)
elif result['classification_confidence'] >= 0.7:
    print("⚠️ 중간 신뢰도 분류")
    process_with_normal_priority(result)
else:
    print("❓ 낮은 신뢰도 분류 - 재확인 필요")
    process_with_verification(result)
```

### 4. 멀티턴 처리

```python
# 대화 히스토리 유지 (수동 구현)
conversation = []

while True:
    user_input = input("질문: ")
    
    # 이전 맥락 포함
    context = "\n".join([f"Q: {c['q']}\nA: {c['a']}" 
                         for c in conversation])
    
    full_query = f"{context}\n\nQ: {user_input}"
    
    result = pipeline.process_question(full_query)
    
    # 히스토리 저장
    conversation.append({
        'q': user_input,
        'a': result['answer']
    })
    
    print(f"A: {result['answer']}\n")
```

---

## 성능 최적화

### 1. 캐싱 활용

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query):
    return pipeline.process_question(query)

# 동일 질문 재조회시 캐시 사용
result1 = cached_search("개 피부염?")
result2 = cached_search("개 피부염?")  # 캐시에서 반환
```

### 2. 배치 처리 활용

```python
# 여러 질문 한 번에 처리
questions = load_questions_from_file("questions.txt")

# 순차 처리 (느림)
# results = [pipeline.process_question(q) for q in questions]

# 배치 처리 (빠름)
results = pipeline.batch_process_questions(questions)
```

### 3. 타입별 핸들러만 사용

```python
# 의료 질문만 처리하는 경우
handler = MedicalQAHandler(vectorstore)

# 분류 오버헤드 제거
result = handler.handle_medical_question(query)
```

---

## 출력 형식 커스터마이징

### JSON 형식

```python
import json

result = pipeline.process_question("개 피부염?")
json_output = json.dumps(result, ensure_ascii=False, indent=2)
print(json_output)
```

### CSV 형식

```python
import csv

results = pipeline.batch_process_questions(questions)

with open("results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Question", "Type", "Confidence", "Answer"])
    
    for r in results:
        writer.writerow([
            r['question'],
            r['classification_type'],
            f"{r['classification_confidence']:.1%}",
            r['answer'][:100]  # 처음 100자
        ])
```

### HTML 리포트

```python
html_template = """
<html>
<body>
<h1>반려동물 QA 결과</h1>
{results_html}
</body>
</html>
"""

results_html = ""
for result in results:
    results_html += f"""
    <div>
        <h3>{result['question']}</h3>
        <p><strong>분류:</strong> {result['classification_type']}</p>
        <p><strong>신뢰도:</strong> {result['classification_confidence']:.1%}</p>
        <p><strong>답변:</strong> {result['answer']}</p>
    </div>
    """

with open("results.html", "w") as f:
    f.write(html_template.format(results_html=results_html))
```

---

## FAQ (자주 묻는 질문)

**Q: 웹 검색은 항상 수행되나요?**
A: 아니요. Type A 의료 질문에서 근거 점수가 0.6 이상이면 내부 데이터만 사용합니다.

**Q: 답변이 틀릴 수 있나요?**
A: 가능합니다. 특히 내부 데이터가 부족한 경우 웹 검색을 활용하며, 항상 의료 전문가 상담을 권장합니다.

**Q: 병원 정보는 얼마나 최신인가요?**
A: 현재 데이터는 서울시 공식 정보 기반입니다. 정기적 업데이트가 필요합니다.

**Q: 비용이 들나요?**
A: OpenAI API 사용료가 발생합니다. (약 $0.02-0.10/질문)

**Q: 로컬에서만 실행되나요?**
A: 벡터스토어는 로컬이지만 LLM은 클라우드(OpenAI)를 사용합니다.

---

**마지막 업데이트**: 2025년 12월 3일

