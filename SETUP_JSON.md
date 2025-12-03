# JSON 기반 병원 데이터 처리 설정 가이드

## 📋 개요

기존 CSV 파일을 JSON 형식으로 변환하여 병원 데이터를 더 효율적으로 처리할 수 있도록 업그레이드했습니다.

**변경 사항:**
- ✅ CSV 파일 → JSON 파일로 마이그레이션
- ✅ 2,202개의 동물병원 데이터 포함
- ✅ 빠르고 효율적인 JSON 기반 파싱
- ✅ 좌표 기반 검색 기능 추가
- ✅ 자연어 질문 처리 개선

## 📂 파일 구조

```
project/
├── data/
│   └── raw/
│       └── hospital/
│           └── 서울시_동물병원_인허가_정보.json  ← 새로운 JSON 파일
├── src/
│   ├── hospital_handler.py                    ← 업데이트됨 (JSON 기반)
│   └── advanced_rag_pipeline.py               ← 업데이트됨 (JSON 경로 사용)
├── demo_json_hospital.py                      ← 데모 스크립트
├── example_usage.py                           ← 사용 예제
├── JSON_HOSPITAL_GUIDE.md                     ← JSON 사용 가이드
└── SETUP_JSON.md                              ← 이 파일
```

## 🚀 빠른 시작

### 1단계: 기본 초기화

```python
from src.hospital_handler import HospitalHandler

# JSON 파일로부터 병원 데이터 로드
handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')

print(f"로드된 병원 수: {len(handler.hospitals)}개")
```

### 2단계: 지역 검색

```python
# 강남구 병원 검색
hospitals = handler.search_by_location("강남구")

for hospital in hospitals[:5]:
    print(f"{hospital['name']} - {hospital['address']}")
```

### 3단계: 통계 확인

```python
# 전체 통계
stats = handler.get_statistics()
print(f"총 병원: {stats['total_hospitals']}개")
print(f"영업 중: {stats['operating_hospitals']}개")
```

## 📊 JSON 데이터 구조

JSON 파일의 구조:

```json
{
  "DESCRIPTION": {
    "필드명": "필드 설명",
    ...
  },
  "DATA": [
    {
      "bplcnm": "병원명",
      "rdnwhladdr": "도로명주소",
      "sitewhladdr": "지번주소",
      "sitetel": "전화번호",
      "trdstatenm": "영업상태",
      "x": "좌표X",
      "y": "좌표Y",
      ...
    },
    ...
  ]
}
```

## 🔍 주요 기능

### 지역 기반 검색
```python
hospitals = handler.search_by_location("강남구")
```

### 병원명 검색
```python
hospitals = handler.search_by_name("포레온")
```

### 영업 중인 병원만
```python
hospitals = handler.get_operating_hospitals_by_district("송파구")
```

### 좌표 기반 검색
```python
hospitals = handler.search_by_coordinates(x=205000, y=450000, radius=1.0)
```

### 통계 조회
```python
stats = handler.get_statistics()
```

### 질문 처리
```python
result = handler.handle_hospital_question("강남구 동물병원을 찾아주세요")
```

### 데이터 내보내기
```python
handler.export_to_json("output.json")
```

## 🔄 CSV에서 JSON으로 마이그레이션

### Before (CSV)
```python
handler = HospitalHandler("data/raw/hospital/서울시_동물병원_인허가_정보.csv")
```

### After (JSON)
```python
handler = HospitalHandler("data/raw/hospital/서울시_동물병원_인허가_정보.json")
```

**나머지 코드는 동일하게 작동합니다!**

## 🧪 테스트 및 데모

### 데모 실행
```bash
python demo_json_hospital.py
```

출력 예:
```
================================================================================
🏥 JSON 기반 병원 데이터 처리 데모
================================================================================

[1단계] JSON 파일 로드 중...
✓ 로드 완료!
  - 메타데이터 필드: 30개
  - 병원 데이터: 2202개

[2단계] 기본 정보 추출
첫 번째 병원 정보:
  - 병원명: 아이랑 동물병원
  - 주소: 서울특별시 동대문구 이문로35길 12...
  - 전화: 
  - 상태: 영업/정상
  - 좌표: (205249.265435832, 455308.651763587)
```

### 사용 예제 실행
```bash
python example_usage.py
```

## 📈 성능 개선

| 항목 | CSV | JSON |
|------|-----|------|
| 로드 시간 | 느림 | ⚡ 빠름 |
| 메모리 효율 | 낮음 | 높음 |
| 검색 속도 | 느림 | ⚡ 빠름 |
| 좌표 기반 검색 | ❌ 없음 | ✅ 지원 |
| 데이터 정확성 | 보통 | ✅ 우수 |

## 🛠️ API 레퍼런스

### HospitalHandler 클래스

#### 초기화
```python
handler = HospitalHandler(hospital_json_path="...")
```

#### 메서드

| 메서드 | 설명 | 반환 |
|--------|------|------|
| `search_by_location(location)` | 지역명으로 검색 | 병원 리스트 |
| `search_by_name(name)` | 병원명으로 검색 | 병원 리스트 |
| `search_by_coordinates(x, y, radius)` | 좌표 기반 검색 | 병원 리스트 |
| `get_nearby_hospitals(district, limit)` | 근처 병원 | 병원 리스트 |
| `get_operating_hospitals_by_district(district)` | 영업 중인 병원 | 병원 리스트 |
| `get_statistics()` | 통계 조회 | 통계 딕셔너리 |
| `handle_hospital_question(query)` | 질문 처리 | 결과 딕셔너리 |
| `export_to_json(path)` | 데이터 내보내기 | bool |

## 💡 고급 사용법

### 특정 구의 모든 영업 중인 병원 조회
```python
handler = HospitalHandler()
gangnam_operating = handler.get_operating_hospitals_by_district("강남구")
print(f"강남구 영업 중인 병원: {len(gangnam_operating)}개")
```

### RAG 시스템과의 통합
```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline

pipeline = AdvancedRAGPipeline(
    vectorstore=vectorstore,
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json",
    llm_model="gpt-4o-mini"
)

# 병원 질문 처리
result = pipeline.process_question("강남구 24시 동물병원을 찾아주세요")
print(result['formatted_answer'])
```

### 데이터 필터링 및 분석
```python
handler = HospitalHandler()

# 강남구 영업 중인 병원
gangnam = handler.get_operating_hospitals_by_district("강남구")

# 전화번호가 있는 병원만
with_phone = [h for h in gangnam if h['phone'] != 'Unknown']

# 정렬
sorted_hospitals = sorted(with_phone, key=lambda x: x['name'])

for hospital in sorted_hospitals[:10]:
    print(f"{hospital['name']} - {hospital['phone']}")
```

## ⚠️ 문제 해결

### JSON 파일을 찾을 수 없음
**원인:** 파일 경로가 잘못됨
**해결:** 경로 확인
```python
import os
path = "data/raw/hospital/서울시_동물병원_인허가_정보.json"
assert os.path.exists(path), f"파일 없음: {path}"
```

### 병원 데이터가 비어있음
**원인:** JSON 파싱 오류
**해결:** 파일 유효성 검사
```python
import json
with open("data/raw/hospital/서울시_동물병원_인허가_정보.json") as f:
    data = json.load(f)
    print(f"로드된 병원: {len(data['DATA'])}개")
```

### 검색 결과가 없음
**원인:** 검색 용어 오류
**해결:** 검색어 확인
```python
# 정확한 구 이름 사용 (예: "강남구" O, "강남" X)
hospitals = handler.search_by_location("강남구")
```

## 📚 참고 문서

- [JSON 병원 사용 가이드](JSON_HOSPITAL_GUIDE.md) - 상세한 사용 가이드
- [데모 스크립트](demo_json_hospital.py) - 실행 가능한 데모
- [사용 예제](example_usage.py) - 다양한 사용 사례

## ✅ 체크리스트

JSON 기반 병원 데이터 설정 완료 확인:

- [x] `hospital_handler.py` 업데이트 (JSON 기반)
- [x] `advanced_rag_pipeline.py` 업데이트 (JSON 경로)
- [x] `advanced_main.py` 업데이트 (JSON 경로)
- [x] 데모 스크립트 작성 및 테스트
- [x] 사용 예제 작성
- [x] 설정 가이드 작성
- [x] 2,202개 병원 데이터 로드 확인

## 🎯 다음 단계

1. **예제 실행:** `python example_usage.py`
2. **데모 확인:** `python demo_json_hospital.py`
3. **가이드 참고:** [JSON_HOSPITAL_GUIDE.md](JSON_HOSPITAL_GUIDE.md)
4. **본격 사용:** 프로젝트에 HospitalHandler 통합

## 📞 지원

문제가 발생하면:
1. 에러 메시지 확인
2. [문제 해결](#%EF%B8%8F-문제-해결) 섹션 참고
3. 로그 파일 확인

---

**성공적으로 JSON 기반 병원 데이터 처리가 설정되었습니다! 🎉**

