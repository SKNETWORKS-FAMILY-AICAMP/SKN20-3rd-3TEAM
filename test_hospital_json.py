"""
JSON 기반 병원 데이터 테스트 스크립트
"""
import sys
from pathlib import Path

# src 모듈 import
sys.path.append(str(Path(__file__).parent))
from src.hospital_handler import HospitalHandler


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=" * 80)
    print("🏥 병원 정보 시스템 - JSON 기반 테스트")
    print("=" * 80)
    
    # 1. 병원 핸들러 초기화
    print("\n[1] 병원 데이터 로드 중...")
    handler = HospitalHandler(
        hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json"
    )
    
    # 2. 통계 출력
    print("\n[2] 전체 통계 조회")
    print("-" * 60)
    stats = handler.get_statistics()
    print(f"총 병원 수: {stats.get('total_hospitals', 0)}")
    print(f"영업 중인 병원: {stats.get('operating_hospitals', 0)}")
    print(f"폐업한 병원: {stats.get('closed_hospitals', 0)}")
    print(f"\n상위 10개 구의 병원 수:")
    for district, count in stats.get('top_districts', [])[:10]:
        print(f"  • {district}: {count}개")
    
    # 3. 특정 지역 검색
    print("\n[3] 강남구 병원 검색")
    print("-" * 60)
    gangnam_hospitals = handler.search_by_location("강남구", limit=5)
    print(f"강남구 병원: {len(gangnam_hospitals)}개 발견")
    for i, hospital in enumerate(gangnam_hospitals[:3], 1):
        print(f"\n  {i}. {hospital.get('name', 'Unknown')}")
        print(f"     주소: {hospital.get('address', 'Unknown')}")
        print(f"     전화: {hospital.get('phone', 'Unknown')}")
        print(f"     상태: {hospital.get('status', 'Unknown')}")
    
    # 4. 병원명 검색
    print("\n[4] 특정 병원 검색 (이름 기반)")
    print("-" * 60)
    search_results = handler.search_by_name("포레온")
    print(f"'포레온' 검색 결과: {len(search_results)}개")
    for hospital in search_results[:3]:
        print(f"\n  • {hospital.get('name', 'Unknown')}")
        print(f"    주소: {hospital.get('address', 'Unknown')}")
        print(f"    좌표: ({hospital.get('coordinates', {}).get('x', 'N/A')}, {hospital.get('coordinates', {}).get('y', 'N/A')})")
    
    # 5. 영업 중인 병원만 조회
    print("\n[5] 송파구 영업 중인 병원")
    print("-" * 60)
    operating_hospitals = handler.get_operating_hospitals_by_district("송파구")
    print(f"송파구 영업 중인 병원: {len(operating_hospitals)}개")
    for i, hospital in enumerate(operating_hospitals[:3], 1):
        print(f"\n  {i}. {hospital.get('name', 'Unknown')}")
        print(f"     주소: {hospital.get('address', 'Unknown')}")
    
    # 6. 병원 질문 처리
    print("\n[6] 병원 질문 처리 테스트")
    print("-" * 60)
    queries = [
        "강남구 동물병원을 찾아주세요",
        "포레온 동물병원의 위치를 알려주세요",
        "서울 병원 정보를 알려줄래요"
    ]
    
    for query in queries:
        print(f"\n질문: {query}")
        result = handler.handle_hospital_question(query)
        print(f"발견된 병원: {len(result.get('hospitals', []))}개")
        print(f"응답:\n{result.get('response', 'N/A')[:200]}...")
    
    # 7. 데이터 내보내기
    print("\n[7] 데이터 내보내기")
    print("-" * 60)
    success = handler.export_to_json("hospitals_export_test.json")
    if success:
        print("✓ 데이터 내보내기 성공!")
    
    print("\n" + "=" * 80)
    print("✓ 모든 테스트 완료!")
    print("=" * 80)


def test_search_operations():
    """검색 기능 상세 테스트"""
    print("\n" + "=" * 80)
    print("🔍 검색 기능 상세 테스트")
    print("=" * 80)
    
    handler = HospitalHandler(
        hospital_json_path="data/raw/hospital/서울시_동물병원_인허가_정보.json"
    )
    
    # 다양한 지역으로 검색
    test_districts = ["강남구", "송파구", "강동구", "관악구"]
    
    print("\n지역별 병원 수 비교:")
    print("-" * 60)
    for district in test_districts:
        hospitals = handler.search_by_location(district)
        print(f"{district}: {len(hospitals)}개")
    
    # 메타데이터 확인
    print("\n병원 데이터 필드 설명:")
    print("-" * 60)
    metadata = handler.get_hospital_metadata_description()
    field_samples = list(metadata.items())[:5]
    for field, description in field_samples:
        print(f"  • {field}: {description}")
    print(f"  ... 등 총 {len(metadata)}개 필드")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_search_operations()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

