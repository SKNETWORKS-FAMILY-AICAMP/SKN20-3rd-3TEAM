"""
공통 유틸리티 함수 모듈
"""
from typing import Dict, List, Optional
from datetime import datetime


def format_hospital_info(hospitals: List[Dict]) -> str:
    """
    병원 정보를 보기 좋게 포맷팅합니다.
    
    Args:
        hospitals: 병원 정보 리스트
        
    Returns:
        str: 포맷팅된 병원 정보 텍스트
        
    Examples:
        >>> hospitals = [
        ...     {
        ...         'name': '행복동물병원',
        ...         'address': '서울시 강남구',
        ...         'phone': '02-123-4567',
        ...         'distance_km': 1.2
        ...     }
        ... ]
        >>> print(format_hospital_info(hospitals))
    """
    if not hospitals:
        return "⚠️ 근처 동물병원 정보를 찾지 못했습니다. '동물병원 + 지역명'으로 직접 검색해 주세요."
    
    result = []
    result.append("\n🏥 **근처 동물병원 추천**\n")
    
    for i, hospital in enumerate(hospitals, 1):
        info_parts = [
            f"\n**{i}. {hospital.get('name', '정보 없음')}**",
            f"   📍 주소: {hospital.get('address', '정보 없음')}"
        ]
        
        # 도로명 주소가 있으면 추가
        if hospital.get('road_address'):
            info_parts.append(f"   🛣️  도로명: {hospital['road_address']}")
        
        # 전화번호
        info_parts.append(f"   📞 전화: {hospital.get('phone', '정보 없음')}")
        
        # 거리 정보
        if hospital.get('distance_km') is not None:
            info_parts.append(f"   📏 거리: 약 {hospital['distance_km']}km")
        
        # 지도 URL
        if hospital.get('map_url'):
            info_parts.append(f"   🗺️  지도: {hospital['map_url']}")
        
        result.append("\n".join(info_parts))
    
    # 안내 메시지
    result.append("\n\n💡 증상이 심각하거나 급격히 악화되는 경우, 위 병원 중 가장 가까운 곳으로 즉시 방문하세요.")
    
    return "\n".join(result)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    텍스트를 지정된 길이로 자릅니다.
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이 (기본값: 200)
        suffix: 말줄임표 (기본값: "...")
        
    Returns:
        str: 잘린 텍스트
        
    Examples:
        >>> long_text = "이것은 매우 긴 텍스트입니다." * 20
        >>> truncate_text(long_text, 50)
        '이것은 매우 긴 텍스트입니다.이것은 매우 긴 텍스트입니다.이것은...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_source_info(sources: List[Dict], show_details: bool = True) -> str:
    """
    RAG 소스 정보를 포맷팅합니다.
    
    Args:
        sources: 소스 정보 리스트
        show_details: 상세 정보 표시 여부
        
    Returns:
        str: 포맷팅된 소스 정보
    """
    if not sources:
        return "참고한 자료가 없습니다."
    
    result = []
    result.append(f"\n📚 **참고 자료** (총 {len(sources)}개)\n")
    
    if show_details:
        for i, source in enumerate(sources, 1):
            disease = source.get('disease', 'Unknown')
            symptom = source.get('symptom', 'Unknown')
            result.append(f"{i}. 질병: {disease} | 증상: {symptom}")
    else:
        result.append(f"VectorDB에서 {len(sources)}개의 관련 문서를 참고했습니다.")
    
    return "\n".join(result)


def format_web_search_results(web_results: List[Dict]) -> str:
    """
    웹검색 결과를 포맷팅합니다.
    
    Args:
        web_results: 웹검색 결과 리스트
        
    Returns:
        str: 포맷팅된 웹검색 결과
    """
    if not web_results:
        return ""
    
    result = []
    result.append("\n\n" + "=" * 50)
    result.append("\n🔍 **웹검색으로 추가 확인한 자료**\n")
    
    for i, item in enumerate(web_results[:3], 1):
        if item.get('url'):
            result.append(f"\n{i}. **{item.get('title', '제목 없음')}**")
            result.append(f"   🔗 출처: {item['url']}")
            
            content_preview = item.get('content', '')
            if content_preview:
                preview = truncate_text(content_preview, 150)
                result.append(f"   💬 요약: {preview}")
        else:
            # AI 요약인 경우
            result.append(f"\n{i}. **{item.get('title', 'AI 요약')}**")
            content = item.get('content', '')
            if content:
                preview = truncate_text(content, 200)
                result.append(f"   💬 {preview}")
    
    return "\n".join(result)


def create_response_header(used_web_search: bool = False) -> str:
    """
    응답 헤더를 생성합니다.
    
    Args:
        used_web_search: 웹검색 사용 여부
        
    Returns:
        str: 포맷팅된 헤더
    """
    header = []
    header.append("=" * 50)
    
    if used_web_search:
        header.append("📊 **정보 출처: VectorDB + 웹검색** 🌐")
        header.append("(VectorDB에 충분한 정보가 없어 웹에서 추가 검색했습니다)")
    else:
        header.append("📊 **정보 출처: VectorDB** 📚")
        header.append("(업로드된 강아지 증상 데이터베이스에서 정보를 가져왔습니다)")
    
    header.append("=" * 50 + "\n")
    
    return "\n".join(header)


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    타임스탬프를 포맷팅합니다.
    
    Args:
        timestamp: datetime 객체 (None이면 현재 시각)
        
    Returns:
        str: 포맷팅된 시각 문자열
        
    Examples:
        >>> format_timestamp()
        '2024-01-15 14:30:25'
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def validate_location(location: Optional[str]) -> str:
    """
    위치 정보를 검증하고 기본값을 반환합니다.
    
    Args:
        location: 위치 문자열
        
    Returns:
        str: 유효한 위치 문자열
    """
    if not location or not location.strip():
        return "서울특별시"
    return location.strip()


def clean_phone_number(phone: str) -> str:
    """
    전화번호를 정리합니다.
    
    Args:
        phone: 원본 전화번호
        
    Returns:
        str: 정리된 전화번호
        
    Examples:
        >>> clean_phone_number("02-123-4567")
        '02-123-4567'
        
        >>> clean_phone_number("")
        '정보 없음'
    """
    if not phone or phone.strip() == "":
        return "정보 없음"
    return phone.strip()


def calculate_distance_text(distance_km: Optional[float]) -> str:
    """
    거리를 텍스트로 변환합니다.
    
    Args:
        distance_km: 킬로미터 단위 거리
        
    Returns:
        str: 거리 텍스트
        
    Examples:
        >>> calculate_distance_text(1.23)
        '약 1.23km'
        
        >>> calculate_distance_text(None)
        '거리 정보 없음'
    """
    if distance_km is None:
        return "거리 정보 없음"
    return f"약 {distance_km}km"


# 테스트용 메인 함수
if __name__ == "__main__":
    # 테스트 데이터
    test_hospitals = [
        {
            'name': '행복동물병원',
            'address': '서울시 강남구 테헤란로 123',
            'phone': '02-123-4567',
            'distance_km': 1.2,
            'map_url': 'https://example.com/map1'
        },
        {
            'name': '사랑동물병원',
            'address': '서울시 송파구 올림픽로 456',
            'phone': '02-234-5678',
            'distance_km': 2.5,
            'map_url': 'https://example.com/map2'
        }
    ]
    
    print("=" * 60)
    print("유틸리티 함수 테스트")
    print("=" * 60)
    
    print("\n[1] 병원 정보 포맷팅:")
    print(format_hospital_info(test_hospitals))
    
    print("\n[2] 텍스트 자르기:")
    long_text = "이것은 매우 긴 텍스트입니다. " * 10
    print(truncate_text(long_text, 50))
    
    print("\n[3] 응답 헤더:")
    print(create_response_header(used_web_search=True))
    
    print("\n[4] 타임스탬프:")
    print(format_timestamp())
    
    print("\n[5] 위치 검증:")
    print(f"빈 문자열: {validate_location('')}")
    print(f"None: {validate_location(None)}")
    print(f"서울시 강남구: {validate_location('서울시 강남구')}")
