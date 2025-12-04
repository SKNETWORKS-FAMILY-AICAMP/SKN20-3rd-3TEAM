"""
카카오맵 기능 테스트 스크립트
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.kakao_map import HospitalMapper
from src.hospital_web_search import (
    HospitalWebSearcher,
    extract_hospital_name_from_question,
    extract_location_from_question
)


def test_hospital_mapper():
    """HospitalMapper 테스트"""
    print("=" * 60)
    print("🧪 HospitalMapper 테스트")
    print("=" * 60)
    
    try:
        # 1. HospitalMapper 초기화
        mapper = HospitalMapper()
        print("✅ HospitalMapper 초기화 성공")
        
        # 2. CSV 파일 로드
        hospital_csv_path = Path(__file__).parent / "data" / "raw" / "hospital" / "서울시_동물병원_인허가_정보.json"
        hospitals = mapper.load_hospitals_from_csv(str(hospital_csv_path))
        print(f"✅ CSV에서 {len(hospitals)}개 병원 로드")
        
        # 3. 첫 번째 병원 정보 확인
        if hospitals:
            first_hospital = hospitals[0]
            info = mapper.get_hospital_info(first_hospital)
            print("\n첫 번째 병원 정보:")
            print(f"  이름: {info['name']}")
            print(f"  주소: {info['address']}")
            print(f"  전화: {info['phone']}")
            print(f"  상태: {info['status']}")
            
            # 4. 전체 통계
            hospitals_info = [mapper.get_hospital_info(h) for h in hospitals]
            print(f"\n📊 통계:")
            print(f"  총 병원 수: {len(hospitals_info)}")
            print(f"  좌표 있는 병원: {sum(1 for h in hospitals_info if h['lat'] and h['lng'])}")
            print(f"  전화번호 있는 병원: {sum(1 for h in hospitals_info if h['phone'])}")
        
        print("\n✅ HospitalMapper 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return False


def test_hospital_web_searcher():
    """HospitalWebSearcher 테스트"""
    print("\n" + "=" * 60)
    print("🧪 HospitalWebSearcher 테스트")
    print("=" * 60)
    
    try:
        # 1. 초기화
        searcher = HospitalWebSearcher()
        print("✅ HospitalWebSearcher 초기화 성공")
        
        # 2. 질문에서 병원명 추출
        question1 = "서울에 있는 ABC동물병원의 위치는 어디인가요?"
        hospital_name = extract_hospital_name_from_question(question1)
        print(f"\n질문: {question1}")
        print(f"추출된 병원명: {hospital_name}")
        
        # 3. 질문에서 지역 추출
        question2 = "부산의 좋은 동물병원을 추천해주세요"
        location = extract_location_from_question(question2)
        print(f"\n질문: {question2}")
        print(f"추출된 지역: {location}")
        
        # 4. 병원 정보 검색 (Tavily API 필요)
        print("\n💡 팁: Tavily API 키가 있으면 실제 웹 검색이 수행됩니다.")
        
        print("\n✅ HospitalWebSearcher 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return False


def test_kakao_api_key():
    """카카오 API 키 확인"""
    print("\n" + "=" * 60)
    print("🧪 카카오맵 API 키 테스트")
    print("=" * 60)
    
    kakao_api_key = os.getenv("KAKAO_API_KEY")
    
    if kakao_api_key:
        # 마스킹된 키 표시
        masked_key = kakao_api_key[:5] + "*" * (len(kakao_api_key) - 10) + kakao_api_key[-5:]
        print(f"✅ KAKAO_API_KEY 설정됨: {masked_key}")
        return True
    else:
        print("⚠️ KAKAO_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 KAKAO_API_KEY=<your-key>를 추가하세요.")
        return False


def main():
    """메인 테스트"""
    print("\n" + "🎉" * 30)
    print("카카오맵 기능 테스트 시작")
    print("🎉" * 30 + "\n")
    
    # 테스트 실행
    results = {
        "API 키 확인": test_kakao_api_key(),
        "HospitalMapper": test_hospital_mapper(),
        "HospitalWebSearcher": test_hospital_web_searcher(),
    }
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    print(f"\n총 {len(results)}개 테스트 중 {total_passed}개 통과")
    
    if total_passed == len(results):
        print("\n🎉 모든 테스트 통과! Streamlit 앱을 실행할 준비가 되었습니다.")
        print("명령어: streamlit run app.py")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 위의 오류 메시지를 확인하세요.")


if __name__ == "__main__":
    main()

