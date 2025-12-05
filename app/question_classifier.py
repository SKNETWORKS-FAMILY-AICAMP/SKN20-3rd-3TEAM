"""
질문 의도 분류 모듈
"""
from typing import Literal


# 의도 타입 정의
IntentType = Literal["medical_consultation", "hospital_search", "general"]


def classify_intent(question: str) -> IntentType:
    """
    질문의 의도를 분류합니다.
    
    Args:
        question: 사용자 질문
        
    Returns:
        IntentType: 분류된 의도
            - "medical_consultation": 강아지 증상 상담
            - "hospital_search": 동물병원 찾기
            - "general": 일반 질문
            
    Examples:
        >>> classify_intent("강아지가 기침을 해요")
        'medical_consultation'
        
        >>> classify_intent("근처 동물병원 어디있어요?")
        'hospital_search'
        
        >>> classify_intent("안녕하세요")
        'general'
    """
    question_lower = question.lower()
    
    # 키워드 정의
    hospital_keywords = [
        "병원", "동물병원", "수의사", "수의원",
        "어디", "위치", "찾아", "추천", "근처"
    ]
    
    medical_keywords = [
        "증상", "아파", "기침", "설사", "구토", 
        "절뚝", "피", "열", "무기력", "다리", 
        "눈", "귀", "호흡", "식욕", "통증"
    ]
    
    # 병원 검색 의도 (병원 키워드만 있고 증상 키워드가 없을 때)
    has_hospital_keyword = any(kw in question_lower for kw in hospital_keywords)
    has_medical_keyword = any(kw in question_lower for kw in medical_keywords)
    
    if has_hospital_keyword and not has_medical_keyword:
        return "hospital_search"
    
    # 의료 상담 의도 (증상 키워드가 있을 때)
    if has_medical_keyword:
        return "medical_consultation"
    
    # 일반 질문
    return "general"


def is_medical_question(question: str) -> bool:
    """
    의료 관련 질문인지 확인합니다.
    
    Args:
        question: 사용자 질문
        
    Returns:
        bool: 의료 질문 여부
        
    Examples:
        >>> is_medical_question("강아지가 설사를 해요")
        True
        
        >>> is_medical_question("안녕하세요")
        False
    """
    return classify_intent(question) == "medical_consultation"


def is_hospital_search(question: str) -> bool:
    """
    병원 검색 질문인지 확인합니다.
    
    Args:
        question: 사용자 질문
        
    Returns:
        bool: 병원 검색 질문 여부
        
    Examples:
        >>> is_hospital_search("근처 동물병원 추천해주세요")
        True
        
        >>> is_hospital_search("강아지가 기침해요")
        False
    """
    return classify_intent(question) == "hospital_search"


def get_intent_description(intent: IntentType) -> str:
    """
    의도에 대한 설명을 반환합니다.
    
    Args:
        intent: 의도 타입
        
    Returns:
        str: 의도 설명
    """
    descriptions = {
        "medical_consultation": "강아지 증상에 대한 의료 상담",
        "hospital_search": "동물병원 찾기 및 추천",
        "general": "일반적인 질문 또는 인사"
    }
    return descriptions.get(intent, "알 수 없는 의도")


# 테스트용 메인 함수
if __name__ == "__main__":
    # 테스트 케이스
    test_questions = [
        "강아지가 기침을 자주 해요",
        "근처 동물병원 어디있어요?",
        "서울 강남구 동물병원 추천해주세요",
        "우리 강아지가 설사를 해요",
        "안녕하세요",
        "강아지가 다리를 절뚝거려요",
        "24시간 응급 동물병원 찾아줘"
    ]
    
    print("=" * 60)
    print("질문 의도 분류 테스트")
    print("=" * 60)
    
    for question in test_questions:
        intent = classify_intent(question)
        description = get_intent_description(intent)
        print(f"\n질문: {question}")
        print(f"의도: {intent}")
        print(f"설명: {description}")
