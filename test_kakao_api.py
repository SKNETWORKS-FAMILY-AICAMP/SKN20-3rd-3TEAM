"""
카카오 지도 API 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 환경 변수 로드
load_dotenv()

# Tools 모듈 import
from src.utils.tools import hospital_recommend_tool

# API 키 확인
kakao_key = os.getenv("KAKAO_REST_API_KEY")
print("=" * 60)
print("카카오 지도 API 테스트")
print("=" * 60)
print(f"API 키 상태: {'✅ 설정됨' if kakao_key else '❌ 설정되지 않음'}")

if not kakao_key:
    print("\n⚠️ KAKAO_REST_API_KEY 환경 변수를 설정해주세요.")
    print("\n설정 방법:")
    print("1. PowerShell: $env:KAKAO_REST_API_KEY='your_key_here'")
    print("2. .env 파일: KAKAO_REST_API_KEY=your_key_here")
    sys.exit(1)

# 테스트 위치 리스트
test_locations = [
    "서울시 강남구 역삼동",
    "서울시 마포구 상암동",
    "부산시 해운대구",
]

print(f"\n테스트 위치: {len(test_locations)}개")
print("=" * 60)

for i, location in enumerate(test_locations, 1):
    print(f"\n[테스트 {i}/{len(test_locations)}] 위치: {location}")
    print("-" * 60)
    
    try:
        result = hospital_recommend_tool.invoke(location)
        print(result)
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    print("-" * 60)

print("\n✅ 테스트 완료!")
