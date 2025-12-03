#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON 기반 병원 데이터 처리 데모
"""

def main():
    """메인 데모 함수"""
    import json
    from pathlib import Path
    
    # JSON 파일 경로
    json_path = Path("data/raw/hospital/서울시_동물병원_인허가_정보.json")
    
    if not json_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {json_path}")
        return
    
    # JSON 데이터 로드
    print("=" * 80)
    print("🏥 JSON 기반 병원 데이터 처리 데모")
    print("=" * 80)
    
    print("\n[1단계] JSON 파일 로드 중...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 데이터 구조 확인
    if isinstance(data, dict):
        description = data.get('DESCRIPTION', {})
        hospitals_list = data.get('DATA', [])
        
        print(f"✓ 로드 완료!")
        print(f"  - 메타데이터 필드: {len(description)}개")
        print(f"  - 병원 데이터: {len(hospitals_list)}개")
    else:
        hospitals_list = data if isinstance(data, list) else []
        print(f"✓ 로드 완료! (병원 수: {len(hospitals_list)}개)")
    
    # 기본 정보 추출
    print("\n[2단계] 기본 정보 추출")
    print("-" * 80)
    
    if hospitals_list:
        first_hospital = hospitals_list[0]
        print(f"첫 번째 병원 정보:")
        print(f"  - 병원명: {first_hospital.get('bplcnm', 'N/A')}")
        print(f"  - 주소: {first_hospital.get('rdnwhladdr', 'N/A')[:60]}...")
        print(f"  - 전화: {first_hospital.get('sitetel', 'N/A')}")
        print(f"  - 상태: {first_hospital.get('trdstatenm', 'N/A')}")
        print(f"  - 좌표: ({first_hospital.get('x', 'N/A')}, {first_hospital.get('y', 'N/A')})")
    
    # 통계 계산
    print("\n[3단계] 통계 분석")
    print("-" * 80)
    
    district_count = {}
    status_count = {}
    operating_count = 0
    closed_count = 0
    
    for hospital in hospitals_list:
        # 구 정보 추출
        address = hospital.get('rdnwhladdr', '') or hospital.get('sitewhladdr', '')
        if address:
            parts = address.split()
            if parts and '구' in parts[0]:
                district = parts[0]
                district_count[district] = district_count.get(district, 0) + 1
        
        # 상태 정보
        status = hospital.get('trdstatenm', '')
        status_count[status] = status_count.get(status, 0) + 1
        
        if '영업' in status:
            operating_count += 1
        elif '폐업' in status:
            closed_count += 1
    
    print(f"총 병원 수: {len(hospitals_list)}개")
    print(f"영업 중: {operating_count}개")
    print(f"폐업: {closed_count}개")
    print(f"구의 개수: {len(district_count)}개")
    
    # 상위 10개 구
    print(f"\n상위 10개 구별 병원 수:")
    top_districts = sorted(district_count.items(), key=lambda x: x[1], reverse=True)[:10]
    for district, count in top_districts:
        print(f"  {district}: {count}개")
    
    # 상태별 분포
    print(f"\n상태별 분포:")
    for status, count in sorted(status_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count}개")
    
    # 특정 지역 검색
    print("\n[4단계] 지역별 검색")
    print("-" * 80)
    
    search_districts = ["강남구", "송파구", "강동구"]
    for district in search_districts:
        count = 0
        for hospital in hospitals_list:
            address = hospital.get('rdnwhladdr', '') or hospital.get('sitewhladdr', '')
            if district in address:
                count += 1
        print(f"{district} 병원: {count}개")
    
    # 병원명 검색
    print("\n[5단계] 병원명 검색 - '포레온'")
    print("-" * 80)
    
    search_results = []
    for hospital in hospitals_list:
        if '포레온' in hospital.get('bplcnm', ''):
            search_results.append(hospital)
    
    print(f"검색 결과: {len(search_results)}개")
    for hospital in search_results:
        print(f"  • {hospital.get('bplcnm', 'N/A')}")
        print(f"    주소: {hospital.get('rdnwhladdr', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("✓ 데모 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

