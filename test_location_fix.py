#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""영등포구 검색 테스트"""

from src.hospital_handler import HospitalHandler

# 핸들러 초기화
print("🔄 병원 데이터 로딩 중...")
handler = HospitalHandler()

print("\n" + "="*80)
print("📝 테스트: 영등포구 동물병원 검색")
print("="*80)

# 영등포구 동물병원 검색
result = handler.handle_hospital_question('서울시 영등포구 근처에 있는 동물병원들 알려줘')

print("\n" + "="*80)
print("📝 검색 결과")
print("="*80)
print(result['response'])

print("\n" + "="*80)
print("🔍 상세 정보")
print("="*80)
print(f"찾은 병원 수: {len(result['hospitals'])}")
if result['hospitals']:
    print("\n검색된 병원 목록:")
    for i, hospital in enumerate(result['hospitals'][:5], 1):
        print(f"\n{i}. {hospital['name']}")
        print(f"   주소: {hospital['address']}")
        print(f"   전화: {hospital['phone']}")
