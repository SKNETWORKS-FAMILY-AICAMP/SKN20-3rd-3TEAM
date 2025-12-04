"""
의도 분류 모듈

사용자의 질문을 분류하여 적절한 처리 방식을 결정합니다.
"""

from typing import Optional

from src.config.logger import get_logger
from src.types.query import ClassificationResult, Query
from src.utils.helpers import extract_keywords, normalize_text

logger = get_logger(__name__)


class QuestionClassifier:
    """
    질문 의도 분류기

    규칙 기반으로 질문을 분류하며, 추후 LLM 기반으로 확장할 수 있습니다.

    분류 카테고리:
        - "medical": 반려동물 의료/건강 관련 질문
        - "hospital": 동물병원 위치/정보 관련 질문
        - "general": 일반 정보 질문
        - "unknown": 분류 불가능한 질문
    """

    # 의료 관련 키워드
    MEDICAL_KEYWORDS = [
        "피부염", "피부", "피", "병", "질병", "감염", "염증", "가려움", "구토",
        "설사", "기침", "재채기", "콧물", "눈물", "발열", "식욕", "체중감소",
        "탈모", "진료", "치료", "증상", "진단", "약", "예방접종", "예방",
        "수술", "응급", "독성", "중독", "알레르기", "알러지", "건강", "의사",
        "의료", "수의", "수의사", "동물의사"
    ]

    # 병원 위치 관련 키워드
    HOSPITAL_KEYWORDS = [
        "병원", "병의원", "클리닉", "의원", "위치", "어디", "근처", "주소",
        "지도", "지역", "구", "시", "동", "번지", "길", "로", "강남", "서초",
        "강북", "도봉", "노원", "성동", "광진", "동대문", "중구", "종로", "서대문",
        "마포", "영등포", "구로", "금천", "동작", "관악", "서초", "강남", "송파",
        "강동", "시내", "도심", "찾기", "검색", "네비", "가기", "가는길", "진로"
    ]

    # 일반 정보 관련 키워드
    GENERAL_KEYWORDS = [
        "뭐", "뭔가", "어떻게", "왜", "언제", "누가", "무엇", "정보", "알아보기",
        "공부", "학습", "교육", "설명", "이해", "이란", "의미", "정의"
    ]

    def __init__(self):
        """분류기 초기화"""
        self.logger = logger

    def classify(self, question: str) -> ClassificationResult:
        """
        질문을 분류합니다.

        Args:
            question: 분류할 질문 텍스트

        Returns:
            ClassificationResult: 분류 결과

        Note:
            현재는 규칙 기반으로 분류하며, 추후 다음과 같이 확장 가능:
            1. LLM 기반 분류 (OpenAI, Claude 등)
            2. SVM/Naive Bayes 등 머신러닝 기반 분류
            3. Fine-tuned 언어 모델 사용
        """
        query = Query(text=question)
        normalized_question = normalize_text(question)

        # 의료 관련 질문 판단
        medical_keywords = extract_keywords(normalized_question, self.MEDICAL_KEYWORDS)
        if len(medical_keywords) >= 1:
            intent = "medical"
            confidence = min(0.99, 0.7 + len(medical_keywords) * 0.1)
            details = {"keywords_found": medical_keywords, "rule_matched": "medical"}

        # 병원 위치 관련 질문 판단
        elif any(keyword in normalized_question for keyword in self.HOSPITAL_KEYWORDS):
            hospital_keywords = extract_keywords(
                normalized_question, self.HOSPITAL_KEYWORDS
            )
            intent = "hospital"
            confidence = min(0.99, 0.7 + len(hospital_keywords) * 0.1)
            details = {"keywords_found": hospital_keywords, "rule_matched": "hospital"}

        # 일반 정보 질문 판단
        elif any(keyword in normalized_question for keyword in self.GENERAL_KEYWORDS):
            intent = "general"
            confidence = 0.6
            details = {"rule_matched": "general"}

        # 분류 불가능
        else:
            intent = "unknown"
            confidence = 0.3
            details = {"rule_matched": "none"}

        # Query 객체에 intent 추가
        query.intent = intent

        result = ClassificationResult(
            query=query,
            intent=intent,
            confidence=confidence,
            details=details,
        )

        self.logger.info(
            f"Classified question as '{intent}' (confidence: {confidence:.2f})"
        )

        return result

    def classify_with_llm(self, question: str) -> ClassificationResult:
        """
        LLM을 사용하여 질문을 분류합니다.

        이 메서드는 향후 LLM 기반 분류 구현을 위한 플레이스홀더입니다.

        Args:
            question: 분류할 질문 텍스트

        Returns:
            ClassificationResult: 분류 결과

        Note:
            구현 예시:
            1. OpenAI API 호출
            2. 프롬프트 작성: "다음 질문을 medical/hospital/general/unknown 중 하나로 분류하세요"
            3. 응답 파싱
            4. 신뢰도 계산

        팀원이 이 메서드를 완성하면 classify() 메서드에서 이를 호출하도록 변경 가능
        """
        raise NotImplementedError(
            "LLM 기반 분류는 아직 구현되지 않았습니다. "
            "팀에서 OpenAI/Claude 등의 API를 연동하여 구현해주세요."
        )

    def add_custom_keywords(
        self, category: str, keywords: list[str]
    ) -> None:
        """
        분류기에 커스텀 키워드를 추가합니다.

        Args:
            category: 카테고리 ("medical", "hospital", "general")
            keywords: 추가할 키워드 리스트
        """
        if category == "medical":
            self.MEDICAL_KEYWORDS.extend(keywords)
        elif category == "hospital":
            self.HOSPITAL_KEYWORDS.extend(keywords)
        elif category == "general":
            self.GENERAL_KEYWORDS.extend(keywords)
        else:
            self.logger.warning(f"Unknown category: {category}")

        self.logger.info(f"Added {len(keywords)} keywords to {category} category")

