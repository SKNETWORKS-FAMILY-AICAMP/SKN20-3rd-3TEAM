#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON 기반 병원 데이터 사용 예제

이 파일은 HospitalHandler를 사용하는 다양한 방법을 보여줍니다.
"""

from src.hospital_handler import HospitalHandler


def example_1_basic_usage():
    """예제 1: 기본 사용법"""
    print("\n" + "=" * 80)
    print("예제 1: 기본 사용법")
    print("=" * 80)
    
    # HospitalHandler 초기화
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 로드된 병원 수 확인
    print(f"\n로드된 병원 수: {len(handler.hospitals)}개")


def example_2_location_search():
    """예제 2: 지역 기반 검색"""
    print("\n" + "=" * 80)
    print("예제 2: 지역 기반 검색")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 강남구 병원 검색
    district = "강남구"
    hospitals = handler.search_by_location(district)
    
    print(f"\n{district} 병원 검색 결과: {len(hospitals)}개")
    
    # 처음 5개 병원 출력
    print(f"\n상위 5개 병원:")
    for i, hospital in enumerate(hospitals[:5], 1):
        print(f"\n{i}. {hospital['name']}")
        print(f"   주소: {hospital['address']}")
        print(f"   전화: {hospital['phone'] if hospital['phone'] else '정보없음'}")
        print(f"   상태: {hospital['status']}")


def example_3_name_search():
    """예제 3: 병원명 검색"""
    print("\n" + "=" * 80)
    print("예제 3: 병원명 검색")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 특정 병원 검색
    search_name = "24시"
    results = handler.search_by_name(search_name)
    
    print(f"\n'{search_name}'를 포함하는 병원: {len(results)}개")
    
    # 처음 3개 결과 출력
    for i, hospital in enumerate(results[:3], 1):
        print(f"\n{i}. {hospital['name']}")
        print(f"   주소: {hospital['address']}")
        print(f"   상태: {hospital['status']}")


def example_4_operating_only():
    """예제 4: 영업 중인 병원만 조회"""
    print("\n" + "=" * 80)
    print("예제 4: 영업 중인 병원만 조회")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 송파구의 영업 중인 병원
    district = "송파구"
    operating = handler.get_operating_hospitals_by_district(district)
    
    print(f"\n{district} 영업 중인 병원: {len(operating)}개")
    
    # 처음 5개 출력
    for i, hospital in enumerate(operating[:5], 1):
        print(f"\n{i}. {hospital['name']}")
        print(f"   주소: {hospital['address']}")
        print(f"   인허가일: {hospital['approval_date']}")


def example_5_statistics():
    """예제 5: 통계 조회"""
    print("\n" + "=" * 80)
    print("예제 5: 통계 조회")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 통계 조회
    stats = handler.get_statistics()
    
    print(f"\n총 병원 수: {stats['total_hospitals']}개")
    print(f"영업 중: {stats['operating_hospitals']}개")
    print(f"폐업: {stats['closed_hospitals']}개")
    
    print(f"\n상위 15개 구:")
    for i, (district, count) in enumerate(stats['top_districts'][:15], 1):
        print(f"  {i:2}. {district}: {count:3}개")


def example_6_nearby_hospitals():
    """예제 6: 인접한 병원 조회"""
    print("\n" + "=" * 80)
    print("예제 6: 인접한 병원 조회")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 강남구 인접 병원
    district = "강남구"
    nearby = handler.get_nearby_hospitals(district, limit=10)
    
    print(f"\n{district} 인접 병원 (상위 10개):")
    for i, hospital in enumerate(nearby[:10], 1):
        print(f"  {i:2}. {hospital['name']}")


def example_7_natural_language():
    """예제 7: 자연어 질문 처리"""
    print("\n" + "=" * 80)
    print("예제 7: 자연어 질문 처리")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 자연어 질문들
    queries = [
        "강남구 동물병원을 찾아주세요",
        "24시 응급진료 병원이 있나요?",
        "포레온 동물병원의 위치는?"
    ]
    
    for query in queries:
        print(f"\n질문: {query}")
        result = handler.handle_hospital_question(query)
        
        print(f"발견된 병원: {len(result['hospitals'])}개")
        
        if result['hospitals']:
            # 처음 2개 병원만 표시
            for hospital in result['hospitals'][:2]:
                print(f"  - {hospital['name']}")


def example_8_export_data():
    """예제 8: 데이터 내보내기"""
    print("\n" + "=" * 80)
    print("예제 8: 데이터 내보내기")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 데이터 내보내기
    export_path = "hospitals_export_example.json"
    success = handler.export_to_json(export_path)
    
    if success:
        print(f"\n✓ 데이터를 {export_path}로 내보냈습니다.")
        print(f"  파일 크기: {__import__('os').path.getsize(export_path)} bytes")


def example_9_coordinates_search():
    """예제 9: 좌표 기반 검색"""
    print("\n" + "=" * 80)
    print("예제 9: 좌표 기반 검색")
    print("=" * 80)
    
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    
    # 특정 좌표 주변의 병원 검색
    # 강남역 근처 (대략적 좌표)
    x, y = 203000, 447000
    radius = 1.0
    
    nearby = handler.search_by_coordinates(x, y, radius)
    
    print(f"\n좌표 ({x}, {y}) 반경 {radius} 내 병원: {len(nearby)}개")
    
    # 거리순으로 정렬된 결과
    for i, hospital in enumerate(nearby[:5], 1):
        distance = hospital.get('distance', 'N/A')
        print(f"  {i}. {hospital['name']} (거리: {distance:.2f})")


def main():
    """모든 예제 실행"""
    print("\n" + "=" * 80)
    print("JSON 기반 병원 데이터 - 사용 예제")
    print("=" * 80)
    
    try:
        example_1_basic_usage()
        example_2_location_search()
        example_3_name_search()
        example_4_operating_only()
        example_5_statistics()
        example_6_nearby_hospitals()
        example_7_natural_language()
        example_8_export_data()
        example_9_coordinates_search()
        
        print("\n" + "=" * 80)
        print("✓ 모든 예제 완료!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

