#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.hospital_handler import HospitalHandler

print("=" * 80)
print("JSON 기반 HospitalHandler 테스트")
print("=" * 80)

try:
    # 1. 핸들러 초기화
    print("\n[1] 핸들러 초기화...")
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    print(f"✓ {len(handler.hospitals)}개 병원 로드됨")
    
    # 2. 통계 조회
    print("\n[2] 통계 조회...")
    stats = handler.get_statistics()
    print(f"✓ 총 병원: {stats['total_hospitals']}개")
    print(f"✓ 운영 중: {stats['operating_hospitals']}개")
    print(f"✓ 폐업: {stats['closed_hospitals']}개")
    print(f"✓ 상위 구 (5개):")
    for district, count in stats['top_districts'][:5]:
        print(f"    - {district}: {count}개")
    
    # 3. 지역 검색
    print("\n[3] 강남구 병원 검색...")
    gangnam = handler.search_by_location("강남구")
    print(f"✓ 발견된 병원: {len(gangnam)}개")
    if gangnam:
        h = gangnam[0]
        print(f"  첫 번째: {h['name']}")
    
    # 4. 병원명 검색
    print("\n[4] 병원명 검색 - '포레온'...")
    search = handler.search_by_name("포레온")
    print(f"✓ 검색 결과: {len(search)}개")
    for h in search:
        print(f"  - {h['name']}: {h['address']}")
    
    # 5. 영업 중인 병원
    print("\n[5] 송파구 영업 중인 병원...")
    operating = handler.get_operating_hospitals_by_district("송파구")
    print(f"✓ 영업 중인 병원: {len(operating)}개")
    if operating:
        print(f"  예: {operating[0]['name']}")
    
    # 6. 질문 처리
    print("\n[6] 병원 질문 처리...")
    result = handler.handle_hospital_question("강남구 동물병원")
    print(f"✓ 처리된 질문: {result['question']}")
    print(f"✓ 발견된 병원: {len(result['hospitals'])}개")
    print(f"✓ 응답 길이: {len(result['response'])}자")
    
    print("\n" + "=" * 80)
    print("✓ 모든 테스트 성공!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

