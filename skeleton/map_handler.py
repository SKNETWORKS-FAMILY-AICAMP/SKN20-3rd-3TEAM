"""
Map Handler Module
지도 및 병원 정보 처리

역할:
  - 사용자 쿼리에서 병원명/위치 추출
  - 지도 API (카카오맵)를 통한 병원 정보 조회
  - 거리 기반 정렬 및 포맷팅
"""

from typing import Optional, List, Dict


def get_map_info(query: str) -> str:
    """
    지도 API를 통해 병원 정보를 조회하고 포맷팅
    
    Args:
        query (str): 사용자 쿼리 (예: "강남역 근처 24시간 동물병원")
        
    Returns:
        str: 포맷된 병원 정보 텍스트
            예: "📍 [1번] OO동물병원\n주소: 서울시...\n거리: 500m\n..."\
    
    처리 순서:
        1️⃣  [병원명 추출] 쿼리에서 병원명 추출 (if present)
        2️⃣  [위치 추출] 쿼리에서 위치 정보 추출 (동, 역, 주소 등)
        3️⃣  [API 호출] 카카오맵 API에 병원 검색 요청
        4️⃣  [결과 수집] Top-K 검색 결과 수집
        5️⃣  [거리 계산] 현재 위치 기준 거리 계산
        6️⃣  [거리 정렬] 거리 순서로 정렬
        7️⃣  [포맷팅] 사용자 친화적으로 포맷
        8️⃣  [반환] 최종 병원 정보 반환
    
    예시:
        입력: "강남역 근처 동물병원"
        
        처리:
        1. 위치: "강남역" 추출
        2. 카카오맵 API: "강남역 동물병원" 검색
        3. 결과: [OO병원 (500m), XX병원 (1.2km), ...]
        
        출력:
        "📍 [1번] OO동물병원
         주소: 서울시 강남구 강남대로 87길...
         거리: 500m (도보 6분)
         전화: 02-123-4567
         
         📍 [2번] XX동물병원
         ..."
    
    TODO:
        - 쿼리 파싱 (위치, 병원명, 특수 조건)
        - 카카오맵 API 호출
        - 거리 계산 (Haversine formula)
        - 결과 포맷팅
    """
    # TODO: 실제 지도 API 호출
    # 1. hospital_name = extract_hospital_name(query)
    # 2. location = extract_location(query)
    # 3. api_results = kakao_map_api.search(query)
    # 4. hospitals = format_map_response(api_results)
    
    # 더미 응답
    hospital_info = f"""
📍 [1번] OO동물병원
주소: 서울시 강남구 강남대로 87길 10
거리: 500m (도보 6분)
전화: 02-123-4567
영업 시간: 24시간 영업

📍 [2번] XX동물병원
주소: 서울시 강남구 테헤란로 123
거리: 1.2km (도보 15분)
전화: 02-234-5678
영업 시간: 10:00 - 20:00

📍 [3번] YY동물병원
주소: 서울시 강남구 강남대로 456
거리: 2.0km (도보 25분)
전화: 02-345-6789
영업 시간: 09:00 - 19:00
"""
    
    print(f"✓ [get_map_info] '{query}' → 병원 정보 조회 완료")
    return hospital_info.strip()


def extract_hospital_name(query: str) -> Optional[str]:
    """
    쿼리에서 병원명 추출
    
    Args:
        query (str): 사용자 쿼리
        
    Returns:
        Optional[str]: 추출된 병원명 (또는 None)
        
    예시:
        입력: "OO동물병원 찾아줘"
        출력: "OO동물병원"
        
        입력: "근처 동물병원 찾아"
        출력: None
    
    TODO:
        - 정규식을 이용한 병원명 추출
        - NER (Named Entity Recognition) 활용
    """
    # TODO: 병원명 추출 로직
    # 정규식: r'(\w+)(동물병원|병원|의원)'
    
    # 더미 로직
    if '동물병원' in query:
        words = query.split()
        for i, word in enumerate(words):
            if '동물병원' in word:
                return words[max(0, i-1)] + '동물병원' if i > 0 else '동물병원'
    
    return None


def extract_location(query: str) -> Optional[str]:
    """
    쿼리에서 위치 정보 추출
    
    Args:
        query (str): 사용자 쿼리
        
    Returns:
        Optional[str]: 추출된 위치 (동, 역, 주소 등)
        
    예시:
        입력: "강남역 근처 동물병원"
        출력: "강남역"
        
        입력: "서울시 강남구 강남대로 근처"
        출력: "서울시 강남구 강남대로"
    
    TODO:
        - 정규식을 이용한 위치 추출
        - 지리 데이터베이스 활용
    """
    # TODO: 위치 추출 로직
    
    # 더미 로직
    location_keywords = ['역', '구', '동', '로', '길', '거리', '근처']
    for kw in location_keywords:
        if kw in query:
            idx = query.find(kw)
            return query[:idx+1]
    
    return None


def format_map_response(hospitals: List[Dict[str, str]]) -> str:
    """
    병원 정보 리스트를 사용자 친화적 텍스트로 포맷
    
    Args:
        hospitals (List[Dict[str, str]]): 병원 정보 딕셔너리 리스트
            각 요소: {
                'name': '병원명',
                'address': '주소',
                'distance': '거리 (m)',
                'phone': '전화번호',
                'hours': '영업 시간'
            }
        
    Returns:
        str: 포맷된 병원 정보 텍스트
    
    예시:
        입력:
        [
            {'name': 'OO병원', 'address': '..', 'distance': 500, ...},
            {'name': 'XX병원', 'address': '..', 'distance': 1200, ...}
        ]
        
        출력:
        "📍 [1번] OO병원\n주소: ...\n..."
    
    TODO:
        - 거리 단위 변환 (m → km)
        - 도보 시간 추정 (거리 ÷ 1.4m/s)
        - 이모지 및 마크다운 포맷팅
    """
    # TODO: 포맷팅 로직
    
    formatted = ""
    for idx, hospital in enumerate(hospitals, 1):
        distance_m = hospital.get('distance', 0)
        distance_str = f"{distance_m}m"
        if distance_m >= 1000:
            distance_str = f"{distance_m/1000:.1f}km"
        
        formatted += f"📍 [{idx}번] {hospital.get('name', '불명')}\n"
        formatted += f"주소: {hospital.get('address', '정보 없음')}\n"
        formatted += f"거리: {distance_str}\n"
        formatted += f"전화: {hospital.get('phone', '정보 없음')}\n"
        formatted += f"영업 시간: {hospital.get('hours', '정보 없음')}\n\n"
    
    return formatted.strip()


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    두 좌표 간의 거리 계산 (Haversine formula)
    
    Args:
        lat1, lon1: 첫 번째 좌표 (위도, 경도)
        lat2, lon2: 두 번째 좌표 (위도, 경도)
        
    Returns:
        float: 거리 (미터 단위)
    
    공식:
        Haversine: a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
                   c = 2 ⋅ atan2( √a, √(1−a) )
                   d = R ⋅ c (R = 지구 반지름 = 6371km)
    
    TODO:
        - Haversine 공식 구현
    """
    # TODO: 거리 계산 로직 (Haversine formula)
    
    # 더미 거리 (대략값)
    distance = ((lat2 - lat1)**2 + (lon2 - lon1)**2) ** 0.5 * 111000
    
    return distance


def get_hospital_by_name(hospital_name: str) -> Optional[Dict[str, str]]:
    """
    병원명으로 특정 병원 정보 조회
    
    Args:
        hospital_name (str): 병원명
        
    Returns:
        Optional[Dict[str, str]]: 병원 정보 딕셔너리 (또는 None)
    
    TODO:
        - 카카오맵 API에서 병원 검색
        - 정확한 이름 매칭
    """
    # TODO: 병원명 기반 검색
    
    hospital = {
        'name': hospital_name,
        'address': '서울시 강남구...',
        'phone': '02-123-4567',
        'distance': 500,
        'hours': '24시간 영업'
    }
    
    return hospital


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """
    테스트 실행 (스켈레톤 데모)
    """
    
    print("\n" + "="*60)
    print("🗺️  Map Handler Module - 테스트")
    print("="*60 + "\n")
    
    test_query = "강남역 근처 동물병원"
    
    print("### 테스트 1: 기본 지도 조회 ###\n")
    map_info = get_map_info(test_query)
    print(map_info)
    print()
    
    print("\n### 테스트 2: 위치 추출 ###\n")
    location = extract_location(test_query)
    print(f"추출된 위치: {location}\n")
    
    print("\n### 테스트 3: 병원명 추출 ###\n")
    hospital_name = extract_hospital_name("OO동물병원 찾아줘")
    print(f"추출된 병원명: {hospital_name}\n")
    
    print("\n### 테스트 4: 거리 계산 ###\n")
    distance = calculate_distance(37.4979, 127.0276, 37.5000, 127.0300)
    print(f"거리: {distance:.0f}m\n")
    
    print("="*60)
    print("✅ 테스트 완료!")
    print("="*60)
