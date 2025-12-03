"""
Agent Tools 모듈
RAG 검색 및 병원 추천 도구 정의
"""

from typing import List, Dict
from langchain_core.tools import tool


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


@tool
def hospital_recommend_tool(
    location: str = "서울",
    department: str = "내과",
    urgency: str = "높음"
) -> List[Dict[str, str]]:
    """
    병원 추천 도구: 지역 및 진료과 기반 동물병원 추천
    
    Args:
        location: 위치 (시/도 또는 구/동)
        department: 진료과
        urgency: 응급도 ("높음", "보통", "낮음")
        
    Returns:
        추천 병원 리스트 (이름, 주소, 전화번호, 24시간 운영 여부)
    """
    print(f"[Hospital Recommend] Location: {location}, Dept: {department}, Urgency: {urgency}")
    
    # TODO: 실제 지도 API (카카오맵, 네이버 지도) 연동
    # 실제 구현에서는 kakao_map_server.py의 API를 호출
    
    # 시뮬레이션 응답
    if urgency == "높음":
        hospitals = [
            {
                "name": "24시 응급 동물병원",
                "address": f"{location} 강남구 역삼동 123-45",
                "phone": "02-1234-5678",
                "24hours": "예",
                "distance": "1.2km"
            },
            {
                "name": "스마일 동물 메디컬 센터",
                "address": f"{location} 강남구 삼성동 678-90",
                "phone": "02-2345-6789",
                "24hours": "예",
                "distance": "2.5km"
            }
        ]
    else:
        hospitals = [
            {
                "name": f"{location} 동물병원",
                "address": f"{location} 논현동 456-78",
                "phone": "02-3456-7890",
                "24hours": "아니오",
                "distance": "0.8km"
            }
        ]
    
    return hospitals
