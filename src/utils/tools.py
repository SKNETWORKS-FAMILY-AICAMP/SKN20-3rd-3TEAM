"""
Agent Tools 모듈
RAG 검색 및 병원 추천 도구 정의
"""

import os
import requests
from typing import List, Dict
from langchain_core.tools import tool

# 카카오 REST API 설정
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_API_URL = "https://dapi.kakao.com/v2/local"
HEADERS = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}


@tool
def rag_search_tool(query: str, department: str = "") -> str:
    """
    RAG 검색 도구: 수의학 지식 베이스에서 관련 정보 검색
    
    Args:
        query: 검색할 증상 또는 질문
        department: 진료과 필터 (선택 사항)
        
    Returns:
        검색된 관련 정보
    """
    # 실제 구현에서는 RAG 파이프라인을 호출
    # 여기서는 시뮬레이션
    
    print(f"[RAG Search] Query: {query}, Department: {department}")
    
    # TODO: 실제 RAG 파이프라인 연동
    # from rag.pipeline import query_rag
    # result = query_rag(rag_chain, query)
    
    # 시뮬레이션 응답
    simulated_response = f"""
    [검색 결과 - {department}과]
    
    증상: {query}
    
    의심 질환:
    - 간 질환 (황달, 구토 동반)
    - 담도 폐쇄
    - 췌장염
    
    주의사항:
    - 황달은 심각한 징후일 수 있습니다.
    - 즉시 수의사 진료가 필요합니다.
    
    권장 조치:
    - 24시간 이내 내과 진료 권장
    - 혈액 검사 및 초음파 검사 필요
    """
    
    return simulated_response


def search_nearby_hospitals(query: str = None, lat: float = None, lon: float = None) -> List[Dict]:
    """
    주소(query) 또는 위도/경도(lat, lon)를 기반으로 주변 5km 이내 동물병원 3곳을 거리순으로 검색합니다.
    
    Args:
        query: 주소 문자열 (예: "서울시 강남구 역삼동"), 선택 사항
        lat: 위도(Latitude), 선택 사항
        lon: 경도(Longitude), 선택 사항
        
    Returns:
        병원 정보 리스트 [{"name": str, "address": str, "distance_m": str}]
    """
    if not KAKAO_REST_API_KEY:
        return [{"error": "API 키가 설정되지 않았습니다."}]
    
    x_coord, y_coord = None, None
    
    # GPS 좌표가 직접 전달된 경우: 바로 사용
    if lat is not None and lon is not None:
        x_coord, y_coord = lon, lat  # 카카오 API는 x=경도, y=위도 순서
        print(f"[GPS 좌표 사용] 위도: {lat}, 경도: {lon}")
    
    # 주소 문자열이 전달된 경우: Geocoding (좌표 변환) 수행
    elif query:
        geocode_url = f"{KAKAO_API_URL}/search/address.json"
        params = {"query": query}
        
        try:
            response = requests.get(geocode_url, headers=HEADERS, params=params)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            print(f"좌표 변환 API 오류: {e}")
            return [{"error": "주소 변환에 실패했습니다."}]

        if not result.get('documents'):
            return [{"error": "유효한 주소를 찾을 수 없습니다."}]

        # 첫 번째 주소의 좌표 사용
        x_coord = result['documents'][0]['x']  # 경도(Longitude)
        y_coord = result['documents'][0]['y']  # 위도(Latitude)
        print(f"[주소 변환 완료] {query} → 위도: {y_coord}, 경도: {x_coord}")
    
    # 좌표를 얻지 못한 경우
    else:
        return [{"error": "검색에 필요한 주소 또는 GPS 좌표가 누락되었습니다."}]
    
    if x_coord is None or y_coord is None:
        return [{"error": "검색에 필요한 좌표를 얻지 못했습니다."}]

    # --- 2단계: 좌표 기준으로 주변 동물병원 키워드 검색 ---
    keyword_url = f"{KAKAO_API_URL}/search/keyword.json"
    keyword_params = {
        "query": "동물병원",
        "category_group_code": "HP8",  # 병원 카테고리
        "x": x_coord,
        "y": y_coord,
        "radius": 5000,              # 반경 5km 이내
        "sort": "distance",          # 거리순 정렬
        "size": 3                    # 최대 3개 결과만 요청
    }
    
    try:
        response = requests.get(keyword_url, headers=HEADERS, params=keyword_params)
        response.raise_for_status()
        hospital_result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"병원 검색 API 오류: {e}")
        return [{"error": "병원 검색에 실패했습니다."}]

    hospitals = []
    for doc in hospital_result.get('documents', []):
        hospitals.append({
            'name': doc.get('place_name'),
            'address': doc.get('road_address_name') or doc.get('address_name'),
            'distance_m': doc.get('distance'),  # distance는 미터 단위로 반환됨
            'phone': doc.get('phone', '전화번호 없음')
        })
    
    return hospitals


@tool
def hospital_recommend_tool(query: str = None, lat: float = None, lon: float = None) -> str:
    """
    LangChain Tool로 사용되며, 검색 결과를 LLM이 읽기 쉽게 문자열로 포맷팅하여 반환합니다.
    
    Args:
        query: 주소 문자열 (예: "서울시 강남구 역삼동"), 선택 사항
        lat: 위도(Latitude), 선택 사항
        lon: 경도(Longitude), 선택 사항
        
    Returns:
        포맷팅된 병원 추천 결과 문자열
    """
    if lat is not None and lon is not None:
        print(f"[Hospital Recommend] GPS: 위도={lat}, 경도={lon}")
    elif query:
        print(f"[Hospital Recommend] 주소: {query}")
    else:
        return "❌ 위치 정보(주소 또는 GPS 좌표)가 필요합니다."
    
    hospital_list = search_nearby_hospitals(query=query, lat=lat, lon=lon)
    
    if hospital_list and hospital_list[0].get("error"):
        return f"❌ 병원 검색에 오류가 발생했습니다: {hospital_list[0]['error']}"

    if not hospital_list:
        return f"'{location_query}' 주변 5km 이내에서 운영 중인 동물병원을 찾을 수 없습니다. 주소를 다시 확인하거나 검색 범위를 넓혀주세요."
        
    formatted_output = [f"📍 사용자 위치 기준 가장 가까운 동물병원 정보입니다:\n"]
    
    for i, hosp in enumerate(hospital_list):
        distance_km = float(hosp['distance_m']) / 1000.0  # 미터를 km로 변환
        formatted_output.append(
            f"{i+1}. **{hosp['name']}**\n"
            f"   - 거리: 약 {distance_km:.2f} km\n"
            f"   - 주소: {hosp['address']}\n"
            f"   - 전화번호: {hosp['phone']}\n"
        )
        
    return "\n".join(formatted_output)
