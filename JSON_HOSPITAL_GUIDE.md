# JSON 기반 병원 데이터 처리 가이드

## 개요

기존 CSV 기반 병원 데이터를 **JSON 포맷**으로 변환하여, 더 빠르고 효율적으로 데이터를 처리할 수 있도록 업데이트했습니다.

## 파일 구조

```
data/raw/hospital/
├── 서울시_동물병원_인허가_정보.json  ← JSON 형식의 병원 데이터 (2,202개 병원)
└── (기존 CSV 파일은 삭제됨)
```

## JSON 데이터 구조

### 파일 형식
```json
{
  "DESCRIPTION": {
    "SITEPOSTNO": "소재지우편번호",
    "BPLCNM": "사업장명",
    "SITETEL": "전화번호",
    "RDNWHLADDR": "도로명주소",
    "SITEWHLADDR": "지번주소",
    ...
  },
  "DATA": [
    {
      "bplcnm": "아이랑 동물병원",
      "rdnwhladdr": "서울특별시 동대문구 이문로35길 12...",
      "sitewhladdr": "서울특별시 동대문구 이문동 257-42...",
      "sitetel": "02-1234-5678",
      "trdstatenm": "영업/정상",
      "dtlstatenm": "정상",
      "apvpermymd": "2025-03-04",
      "x": "205249.265435832",
      "y": "455308.651763587",
      ...
    },
    ...
  ]
}
```

## HospitalHandler 클래스 사용법

### 1. 기본 초기화

```python
from src.hospital_handler import HospitalHandler

# JSON 파일로부터 병원 데이터 로드
handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')

print(f"로드된 병원 수: {len(handler.hospitals)}")
```

### 2. 지역 기반 검색

```python
# 특정 구의 병원 검색
gangnam_hospitals = handler.search_by_location("강남구")

for hospital in gangnam_hospitals[:5]:
    print(f"병원명: {hospital['name']}")
    print(f"주소: {hospital['address']}")
    print(f"전화: {hospital['phone']}")
    print(f"상태: {hospital['status']}")
    print(f"좌표: ({hospital['coordinates']['x']}, {hospital['coordinates']['y']})")
    print()
```

### 3. 병원명 검색

```python
# 특정 병원명으로 검색
search_results = handler.search_by_name("포레온")

for hospital in search_results:
    print(f"{hospital['name']} - {hospital['address']}")
```

### 4. 영업 중인 병원만 조회

```python
# 특정 구의 영업 중인 병원만 조회
operating_hospitals = handler.get_operating_hospitals_by_district("송파구")

print(f"송파구 영업 중인 병원: {len(operating_hospitals)}개")
for hospital in operating_hospitals[:3]:
    print(f"  {hospital['name']}")
```

### 5. 통계 조회

```python
# 전체 통계 조회
stats = handler.get_statistics()

print(f"총 병원 수: {stats['total_hospitals']}개")
print(f"영업 중: {stats['operating_hospitals']}개")
print(f"폐업: {stats['closed_hospitals']}개")
print(f"\n상위 10개 구:")
for district, count in stats['top_districts']:
    print(f"  {district}: {count}개")
```

### 6. 좌표 기반 검색

```python
# 특정 좌표 근처의 병원 검색 (반경 1.0)
nearby = handler.search_by_coordinates(x=205000, y=450000, radius=1.0)

print(f"근처 병원: {len(nearby)}개")
for hospital in nearby:
    print(f"{hospital['name']} (거리: {hospital['distance']:.2f})")
```

### 7. 데이터 내보내기

```python
# 처리된 병원 데이터를 새로운 JSON으로 내보내기
success = handler.export_to_json("hospitals_export.json")

if success:
    print("데이터 내보내기 완료!")
```

### 8. 병원 질문 처리

```python
# 자연어 질문으로 병원 검색
query = "강남구 동물병원을 찾아주세요"
result = handler.handle_hospital_question(query)

print(f"발견된 병원: {len(result['hospitals'])}개")
print(f"\n답변:\n{result['response']}")
```

## 주요 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `search_by_location(location)` | 지역명으로 병원 검색 | 병원 정보 리스트 |
| `search_by_name(name)` | 병원명으로 검색 | 병원 정보 리스트 |
| `search_by_coordinates(x, y, radius)` | 좌표 기반 검색 | 병원 정보 리스트 |
| `get_nearby_hospitals(district, limit)` | 구의 병원 목록 조회 | 병원 정보 리스트 |
| `get_operating_hospitals_by_district(district)` | 영업 중인 병원만 조회 | 병원 정보 리스트 |
| `get_statistics()` | 전체 통계 조회 | 통계 정보 딕셔너리 |
| `handle_hospital_question(query)` | 자연어 질문 처리 | 처리 결과 딕셔너리 |
| `export_to_json(path)` | 데이터 내보내기 | 성공 여부 |

## 반환되는 병원 정보 구조

```python
{
    'name': '병원명',
    'address': '주소',
    'phone': '전화번호',
    'status': '영업상태명',
    'state': '상세영업상태명',
    'approval_date': '인허가일자',
    'coordinates': {
        'x': '경도',
        'y': '위도'
    }
}
```

## 사용 예제

### 예제 1: 특정 지역의 모든 동물병원 조회

```python
from src.hospital_handler import HospitalHandler

handler = HospitalHandler()

# 강남구의 모든 병원
gangnam = handler.search_by_location("강남구")

# 영업 중인 병원만 필터링
for hospital in gangnam:
    if '영업' in hospital['status']:
        print(f"{hospital['name']} - {hospital['address']}")
```

### 예제 2: 구별 병원 개수 비교

```python
handler = HospitalHandler()
stats = handler.get_statistics()

# 구별 병원 수 출력
for district, count in sorted(stats['top_districts'], key=lambda x: x[1], reverse=True):
    print(f"{district}: {count}개")
```

### 예제 3: RAG 시스템과 통합

```python
from src.advanced_rag_pipeline import AdvancedRAGPipeline

# JSON 경로로 파이프라인 초기화
pipeline = AdvancedRAGPipeline(
    vectorstore=vectorstore,
    hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json",
    llm_model="gpt-4o-mini"
)

# 병원 관련 질문 처리
result = pipeline.process_question("강남구 동물병원을 찾아주세요")
print(result['formatted_answer'])
```

## 성능 개선 사항

JSON 기반 처리의 장점:

1. **빠른 로드 시간**: 구조화된 JSON으로 파싱 시간 단축
2. **메모리 효율성**: 전체 데이터를 메모리에 유지하면서도 효율적인 검색
3. **좌표 기반 검색**: 지리적 위치 기반 병원 검색 가능
4. **정확한 상태 관리**: 영업/폐업 상태를 정확하게 구분

## 데이터 필드 설명

JSON 데이터의 주요 필드:

- `bplcnm`: 사업장명 (병원명)
- `rdnwhladdr`: 도로명 주소 (주사용)
- `sitewhladdr`: 지번 주소
- `sitetel`: 전화번호
- `trdstatenm`: 영업상태명 ('영업/정상', '폐업' 등)
- `dtlstatenm`: 상세영업상태명
- `apvpermymd`: 인허가일자
- `x`, `y`: 좌표 정보 (WGS84)
- `mgtno`: 관리번호
- `opnsfteamcode`: 개방자치단체코드

## 문제 해결

### JSON 파일을 찾을 수 없음

```python
# 경로 확인
import os
path = "data/raw/hospital/서울시_동물병원_인허가_정보.json"
if os.path.exists(path):
    print("파일 존재")
else:
    print("파일 없음")
```

### 병원 데이터가 비어있음

```python
# 데이터 로드 확인
handler = HospitalHandler()
if len(handler.hospitals) == 0:
    print("데이터 로드 실패")
    print(f"메타데이터: {handler.metadata}")
```

## 마이그레이션 가이드 (CSV → JSON)

기존 CSV 코드에서 JSON으로 변환하려면:

```python
# Before (CSV 기반)
from src.hospital_handler import HospitalHandler
handler = HospitalHandler("data/raw/hospital/서울시_동물병원_인허가_정보.csv")

# After (JSON 기반)
from src.hospital_handler import HospitalHandler
handler = HospitalHandler("data/raw/hospital/서울시_동물병원_인허가_정보.json")

# 나머지 코드는 동일하게 동작
```

## 참고사항

- JSON 파일은 2,202개의 동물병원 데이터를 포함
- 마지막 업데이트: 2025년
- 좌표는 WGS84 좌표계 사용
- 모든 메서드는 대소문자 구분하지 않음

