# 🗺️ 카카오맵 통합 가이드

Streamlit 의료 RAG 애플리케이션에 카카오맵 병원 위치 표시 기능을 추가했습니다.

## 📋 주요 기능

### 1. **CSV 데이터 활용**
- `data/raw/hospital/서울시_동물병원_인허가_정보.json` 파일에서 도로명 주소 자동 로드
- 영업 중인 병원만 필터링하여 표시

### 2. **웹 검색 통합**
- 사용자가 특정 병원명을 언급하면 자동으로 웹에서 주소 검색
- Tavily API를 활용한 실시간 정보 수집

### 3. **카카오맵 시각화**
- 인터랙티브한 지도 표시
- 마커 클릭 시 병원 정보 표시
- 병원 목록 리스트 표시

## 🔧 설정 방법

### 1단계: 환경 변수 설정

`.env` 파일에 카카오맵 API 키 추가:

```bash
KAKAO_API_KEY=your-kakao-map-api-key-here
```

카카오맵 API 키 발급:
- [Kakao Developers](https://developers.kakao.com/)에서 계정 생성
- 새 애플리케이션 등록
- JavaScript 키 복사

### 2단계: 패키지 설치

```bash
pip install -r requirements.txt
```

필수 패키지:
- `streamlit`: 웹 인터페이스
- `pandas`: CSV 데이터 처리
- `requests`: HTTP 요청
- `python-dotenv`: 환경변수 로드

## 🚀 사용 방법

### 기본 사용

```bash
streamlit run app.py
```

### 카카오맵 표시

#### 방법 1: 전체 병원 목록 보기
1. 앱 실행
2. **"🗺️ 동물병원 위치 지도 보기"** 버튼 클릭
3. 인터랙티브 카카오맵 표시

#### 방법 2: 특정 병원 검색
1. 질문에 병원명 포함: "서울에 있는 ABC동물병원의 위치는?"
2. AI가 자동으로 병원 정보 검색
3. 검색 결과가 있으면 지도에 표시

### 예시 질문

```
1. "강아지 피부질환으로 병원을 찾아주세요"
   → 전체 병원 목록 표시

2. "서울의 VIP동물의료센터는 어디에 있나요?"
   → VIP동물의료센터 정보 검색 및 지도 표시

3. "부산 지역 동물병원을 알려주세요"
   → 부산 지역 병원 검색
```

## 📚 모듈 구조

### `src/kakao_map.py`
카카오맵 기능의 핵심 모듈

```python
# 주요 클래스
class HospitalMapper:
    def load_hospitals_from_csv(csv_path: str) -> List[Dict]
        # CSV/JSON 파일에서 병원 정보 로드
    
    def create_kakao_map_html(hospitals: List[Dict]) -> str
        # 독립 실행형 HTML 생성
    
    def create_streamlit_html_component(hospitals: List[Dict]) -> str
        # Streamlit 컴포넌트용 HTML 생성
```

### `src/hospital_web_search.py`
웹 검색을 통한 병원 정보 조회

```python
# 주요 클래스
class HospitalWebSearcher:
    def search_hospital_info(name: str, location: str) -> Dict
        # 병원명과 지역으로 검색
    
    def search_hospital_address(name: str, location: str) -> Optional[str]
        # 도로명 주소만 검색

# 헬퍼 함수
def extract_hospital_name_from_question(question: str) -> Optional[str]
    # 질문에서 병원명 추출
    
def extract_location_from_question(question: str) -> str
    # 질문에서 지역명 추출
```

## 🎨 UI 컴포넌트

### 카카오맵
- 인터랙티브 지도 (높이: 700px)
- 마커 클릭 시 병원 정보창 표시
- 모든 마커를 보이도록 자동 범위 조정

### 병원 목록
- 이름, 주소, 전화번호 표시
- 처음 20개 병원만 표시
- 펼쳐보기(Expander) 형식

### 검색 결과 탭
- **"🔍 검색 결과"**: 특정 병원 정보
- **"📍 전체 병원"**: 전체 병원 목록

## ⚙️ 설정 옵션

### 지도 중심 위치 변경

```python
# app.py의 display_hospital_map 함수에서
display_hospital_map(
    hospitals=None,
    center_lat=37.5665,  # 서울의 위도
    center_lng=126.9780   # 서울의 경도
)
```

### 지도 줌 레벨
- 레벨 1-5: 대역대 지도
- 레벨 6-10: 도시 지도
- 레벨 11-14: 거리 지도
- 레벨 15+: 건물 지도

## 🐛 트러블슈팅

### "KAKAO_API_KEY not found"
✅ 해결:
1. `.env` 파일 생성 확인
2. `KAKAO_API_KEY=` 라인 확인
3. API 키 유효성 확인

### 카카오맵이 표시되지 않음
✅ 해결:
1. 브라우저 개발자 도구의 콘솔 확인
2. 커스텀 도메인이 API 키에 등록되어 있는지 확인
3. 네트워크 연결 상태 확인

### "표시할 병원 정보가 없습니다"
✅ 해결:
1. CSV 파일 경로 확인: `data/raw/hospital/서울시_동물병원_인허가_정보.json`
2. 파일 인코딩 확인 (UTF-8)
3. 좌표 정보(X, Y) 유무 확인

### 병원 검색 결과가 없음
✅ 해결:
1. 정확한 병원명 사용 ("ABC동물병원", "XYZ의료센터" 등)
2. Tavily API 키 확인 (웹 검색용)
3. 인터넷 연결 상태 확인

## 🔌 API 연동

### 카카오맵 API
- **문서**: https://developers.kakao.com/docs/latest/ko/map/common
- **사용 한계**: 월 300만 건
- **응답 시간**: ~100ms

### Tavily 검색 API
- **문서**: https://tavily.com/
- **무료 한계**: 월 1000건 검색
- **응답 시간**: ~200-500ms

## 📊 데이터 형식

### CSV (JSON) 형식
```json
{
  "DATA": [
    {
      "bplcnm": "병원명",
      "rdnwhladdr": "서울특별시 강남구 도곡로 167, 성우빌딩 2층",
      "sitetel": "02-xxxx-xxxx",
      "trdstategbn": "01",  // 01: 영업, 03: 폐업
      "y": "443285.630755972",  // 위도
      "x": "203285.044272499"   // 경도
    }
  ]
}
```

### 병원 정보 객체
```python
{
    'name': '병원명',                    # 사업장명
    'address': '도로명주소',            # rdnwhladdr
    'phone': '전화번호',                # sitetel
    'lat': 37.5665,                     # y 좌표
    'lng': 126.9780,                    # x 좌표
    'status': '영업 중',                # trdstategbn
}
```

## 💡 팁과 트릭

### 1. 성능 최적화
- 대량의 마커 표시 시 지도 줌 레벨 자동 조정
- 처음 20개 병원만 리스트에 표시

### 2. 사용자 경험
- 마커 클릭 시 자동으로 정보창 열기
- 검색 결과와 전체 목록 탭으로 구분

### 3. 데이터 관리
- 폐업한 병원은 자동 필터링
- 좌표 없는 병원은 지도에 표시 안 함

## 🎯 향후 개선 사항

- [ ] 거리 계산 및 최근 병원 추천
- [ ] 병원 리뷰/평점 표시
- [ ] 시간대별 운영 정보
- [ ] 진료과목별 필터링
- [ ] 여러 병원 비교 기능
- [ ] 경로 탐색 (길찾기)

## 📞 지원

문제가 발생하면:
1. `.env` 파일 확인
2. 콘솔 로그 확인
3. Streamlit 재시작 (Ctrl+C → streamlit run app.py)

