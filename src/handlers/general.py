"""
일반 질문 처리 핸들러 (타입 C)
특정 전문가 없이 일반 LLM으로 처리
"""
from typing import Dict, Any
from datetime import datetime
from .base import BaseHandler
from src.llm import get_llm_client
from src.utils import get_logger

logger = get_logger(__name__)


class GeneralHandler(BaseHandler):
    """일반 질문 처리 핸들러"""
    
    def __init__(self, llm_model: str = "gpt-4o-mini"):
        """
        Args:
            llm_model: LLM 모델명
        """
        self.llm = get_llm_client(model=llm_model, temperature=0.0)
        logger.info(f"GeneralHandler 초기화: model={llm_model}")
    
    def handle(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        일반 질문 처리 메인 함수
        
        Args:
            query: 사용자 질문
            **kwargs: 추가 파라미터 (무시됨)
            
        Returns:
            처리 결과 딕셔너리
        """
        logger.info(f"일반 질문 처리 시작: {query[:50]}...")
        
        result = {
            'question': query,
            'question_type': 'C',
            'timestamp': datetime.now().isoformat(),
            'answer': '',
            'sources': [],
            'used_external_search': False
        }
        
        # 프롬프트 구성
        general_prompt = f"""당신은 반려동물 전문 QA 어시스턴트입니다.
다음 질문에 대해 정확하고 도움이 되는 답변을 제공하세요.

질문: {query}

주의:
- 의료 관련 질문이 아님을 확인했습니다.
- 정확하고 신뢰할 수 있는 정보 제공
- 필요시 전문가 상담 권유
- 명확하고 이해하기 쉬운 한국어 사용"""
        
        logger.debug("LLM으로 답변 생성 중...")
        
        try:
            answer = self.llm.invoke(general_prompt)
            result['answer'] = answer
            logger.info("답변 생성 완료")
        except Exception as e:
            logger.error(f"답변 생성 실패: {str(e)}")
            result['answer'] = "죄송하지만 답변을 생성하는 중 오류가 발생했습니다."
        
        return result

