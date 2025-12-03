#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.hospital_handler import HospitalHandler

print("=" * 80)
print("JSON 기반 병원 데이터 테스트")
print("=" * 80)

# 병원 핸들러 초기화
handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')

print(f"\n✓ 로드된 병원 수: {len(handler.hospitals)}")

# 통계 조회
stats = handler.get_statistics()
print(f"✓ 총 병원: {stats['total_hospitals']}개")
print(f"✓ 운영 중: {stats['operating_hospitals']}개")
print(f"✓ 폐업: {stats['closed_hospitals']}개")

# 강남구 검색
print("\n[강남구 병원 검색]")
gangnam = handler.search_by_location("강남구")
print(f"발견된 병원: {len(gangnam)}개")
if gangnam:
    first = gangnam[0]
    print(f"1번 병원: {first['name']}")
    print(f"주소: {first['address']}")
    print(f"전화: {first['phone']}")

# 병원명 검색
print("\n[병원명 검색 - '포레온']")
search = handler.search_by_name("포레온")
print(f"검색 결과: {len(search)}개")
for h in search:
    print(f"  - {h['name']}: {h['address']}")

print("\n✓ 테스트 완료!")

