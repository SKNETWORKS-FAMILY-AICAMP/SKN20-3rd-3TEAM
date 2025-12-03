#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

# JSON 파일 검증
json_path = 'data/raw/hospital/서울시_동물병원_인허가_정보.json'

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("JSON 파일 로드 성공!")
    
    if isinstance(data, dict):
        print(f"  - 구조: Dictionary")
        if 'DESCRIPTION' in data:
            print(f"  - DESCRIPTION 필드: {len(data['DESCRIPTION'])}개 항목")
        if 'DATA' in data:
            print(f"  - DATA 필드: {len(data['DATA'])}개 병원")
            first_hospital = data['DATA'][0]
            print(f"\n첫 번째 병원:")
            print(f"  - 병원명: {first_hospital.get('bplcnm', 'N/A')}")
            print(f"  - 주소: {first_hospital.get('rdnwhladdr', first_hospital.get('sitewhladdr', 'N/A'))}")
            print(f"  - 전화: {first_hospital.get('sitetel', 'N/A')}")
            print(f"  - 상태: {first_hospital.get('trdstatenm', 'N/A')}")
    
except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()

