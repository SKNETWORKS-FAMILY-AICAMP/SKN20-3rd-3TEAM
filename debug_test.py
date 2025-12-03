#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# 출력을 파일로 리디렉트
output_file = open('debug_output.txt', 'w', encoding='utf-8')

try:
    print("=" * 80, file=output_file)
    print("JSON 기반 HospitalHandler 테스트", file=output_file)
    print("=" * 80, file=output_file)
    
    from src.hospital_handler import HospitalHandler
    
    print("\n[1] 핸들러 초기화...", file=output_file)
    handler = HospitalHandler('data/raw/hospital/서울시_동물병원_인허가_정보.json')
    print(f"✓ {len(handler.hospitals)}개 병원 로드됨", file=output_file)
    
    print("\n[2] 통계 조회...", file=output_file)
    stats = handler.get_statistics()
    print(f"✓ 총 병원: {stats['total_hospitals']}개", file=output_file)
    print(f"✓ 운영 중: {stats['operating_hospitals']}개", file=output_file)
    print(f"✓ 폐업: {stats['closed_hospitals']}개", file=output_file)
    
    print("\n[3] 강남구 병원 검색...", file=output_file)
    gangnam = handler.search_by_location("강남구")
    print(f"✓ 발견된 병원: {len(gangnam)}개", file=output_file)
    
    print("\n[4] 병원명 검색...", file=output_file)
    search = handler.search_by_name("포레온")
    print(f"✓ 검색 결과: {len(search)}개", file=output_file)
    for h in search:
        print(f"  - {h['name']}", file=output_file)
    
    print("\n✓ 테스트 완료!", file=output_file)
    
except Exception as e:
    print(f"\n❌ 오류: {e}", file=output_file)
    import traceback
    traceback.print_exc(file=output_file)

finally:
    output_file.close()
    print("결과가 debug_output.txt에 저장되었습니다.")

