"""
🐾 반려동물 의료 RAG 어시스턴트 - CLI 인터페이스
"""

import os
from dotenv import load_dotenv

# 환경 설정
load_dotenv()

def check_requirements():
    """필수 환경 변수 및 패키지 확인"""
    print("\n🔍 환경 확인 중...\n")
    
    # API 키 확인
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY 환경 변수 설정 필수")
        print("   .env 파일에 추가: OPENAI_API_KEY=sk-...")
        return False
    
    if not os.environ.get('TAVILY_API_KEY'):
        print("❌ TAVILY_API_KEY 환경 변수 설정 필수")
        print("   .env 파일에 추가: TAVILY_API_KEY=...")
        return False
    
    print("✅ API 키 확인 완료")
    
    # 필수 패키지 확인
    required_packages = [
        'langchain_core',
        'langchain_openai',
        'langchain_chroma',
        'langchain_community',
        'langgraph',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"\n❌ 누락된 패키지: {', '.join(missing)}")
        print("   실행: pip install -r requirements_langgraph.txt")
        return False
    
    print("✅ 필수 패키지 확인 완료\n")
    return True

def main():
    """메인 CLI 함수"""
    
    # 환경 확인
    if not check_requirements():
        return
    
    print("🚀 반려동물 의료 RAG 어시스턴트 시작 중...\n")
    
    # 워크플로우 임포트
    try:
        from pet_medical_rag_langgraph import app, run_pet_medical_rag
        print("✅ RAG 어시스턴트 로드 완료\n")
    except Exception as e:
        print(f"❌ 로드 실패: {e}")
        return
    
    # CLI 모드
    print("="*70)
    print("🐾 반려동물 의료 RAG 어시스턴트에 오신 것을 환영합니다!")
    print("="*70)
    print("\n📝 질문을 입력하세요. (종료: 'quit' 또는 'exit')\n")
    
    while True:
        try:
            question = input("🐶 질문: ").strip()
            
            if not question:
                print("❓ 질문을 입력해주세요.\n")
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 어시스턴트를 종료합니다.")
                break
            
            # 질문 처리
            run_pet_medical_rag(question)
            
        except KeyboardInterrupt:
            print("\n\n👋 어시스턴트를 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}\n")
            print("다시 시도해주세요.\n")

if __name__ == "__main__":
    main()

