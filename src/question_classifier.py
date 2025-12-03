"""
질문 유형 분류 모듈
의료(A) / 병원(B) / 일반(C) 질문 분류
"""
from enum import Enum
from typing import Tuple, Optional
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class QuestionType(Enum):
    """질문 유형"""
    MEDICAL = "A"  # 반려동물 의료 질문
    HOSPITAL = "B"  # 동물병원/지도 관련 질문
    GENERAL = "C"  # 일반 질문


class QuestionClassifier:
    """질문 분류 클래스"""
    
    def __init__(self, llm_model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.0)
        
        # 키워드 기반 분류용 정규표현식 패턴
        self.medical_keywords = [
            r'증상', r'질병', r'질환', r'병', r'치료', r'진단', r'수술',
            r'약물', r'주사', r'백신', r'예방', r'감염', r'염증', r'통증',
            r'피부', r'귀', r'눈', r'치아', r'간', r'신장', r'심장',
            r'소화', r'호흡', r'면역', r'혈액', r'종양', r'암', r'안락사',
            r'응급', r'사료', r'영양', r'알러지', r'감염병', r'기생충'
        ]
        
        self.hospital_keywords = [
            r'동물병원', r'병원', r'수의사', r'진료', r'위치', r'지도', r'주소',
            r'전화', r'영업', r'시간', r'예약', r'근처', r'주변', r'찾기',
            r'개인동물', r'통합의료', r'응급진료', r'야간진료'
        ]
    
    def _check_keywords(self, text: str, keywords: list[str]) -> float:
        """텍스트에서 키워드 매칭 비율 계산"""
        matched_count = 0
        for keyword in keywords:
            if re.search(keyword, text, re.IGNORECASE):
                matched_count += 1
        return matched_count / len(keywords) if keywords else 0
    
    def _classify_with_llm(self, query: str) -> QuestionType:
        """LLM을 사용하여 질문 분류"""
        classification_prompt = f"""당신은 반려동물 QA 시스템의 질문 분류 전문가입니다.
다음 질문을 분류하세요:

질문: {query}

분류 규칙:
- (A) 의료 관련: 증상, 질병, 치료, 진단, 예방, 약물 등 반려동물 의료 관련 질문
- (B) 병원/지도: 동물병원 위치, 주소, 전화, 진료 정보, 지도 관련 질문
- (C) 일반: 위의 범주에 속하지 않는 일반적인 질문

응답 형식: 
{{
    "classification": "A" or "B" or "C",
    "confidence": 0.0-1.0,
    "reason": "분류 이유"
}}"""
        
        response = self.llm.invoke([HumanMessage(content=classification_prompt)])
        
        try:
            result = json.loads(response.content)
            classification = result.get("classification", "C")
            
            if classification == "A":
                return QuestionType.MEDICAL
            elif classification == "B":
                return QuestionType.HOSPITAL
            else:
                return QuestionType.GENERAL
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본값
            return QuestionType.GENERAL
    
    def classify(self, query: str) -> Tuple[QuestionType, float, str]:
        """
        질문을 분류
        
        Args:
            query: 사용자 질문
            
        Returns:
            (질문유형, 신뢰도, 사유) 튜플
        """
        # 1단계: 키워드 기반 분류
        medical_score = self._check_keywords(query, self.medical_keywords)
        hospital_score = self._check_keywords(query, self.hospital_keywords)
        
        # 키워드 점수가 0.3 이상이면 해당 분류 선택
        if medical_score >= 0.3 and medical_score > hospital_score:
            return QuestionType.MEDICAL, medical_score, "키워드 기반 의료 질문"
        elif hospital_score >= 0.3 and hospital_score > medical_score:
            return QuestionType.HOSPITAL, hospital_score, "키워드 기반 병원 질문"
        
        # 2단계: LLM 기반 분류 (확실하지 않은 경우)
        question_type = self._classify_with_llm(query)
        confidence = max(medical_score, hospital_score)
        
        if question_type == QuestionType.MEDICAL:
            reason = "LLM 기반 의료 질문 분류"
        elif question_type == QuestionType.HOSPITAL:
            reason = "LLM 기반 병원 질문 분류"
        else:
            reason = "LLM 기반 일반 질문 분류"
        
        return question_type, confidence, reason

