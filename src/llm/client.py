"""
LLM 클라이언트
OpenAI ChatGPT 모델 래퍼
"""
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import get_settings
from src.utils import get_logger

logger = get_logger(__name__)


class LLMClient:
    """LLM (Language Model) 클라이언트"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None
    ):
        """
        Args:
            model: 모델명 (기본값: settings에서 로드)
            temperature: 온도 (기본값: settings에서 로드)
            api_key: API 키 (기본값: settings에서 로드)
        """
        settings = get_settings()
        
        self.model = model or settings.llm.model
        self.temperature = temperature if temperature is not None else settings.llm.temperature
        self.api_key = api_key or settings.llm.api_key
        
        if not self.api_key:
            raise ValueError("OpenAI API 키가 설정되지 않았습니다")
        
        self.client = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=self.api_key
        )
        
        logger.info(f"LLMClient 초기화: model={self.model}, temperature={self.temperature}")
    
    def invoke(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        LLM에 메시지를 보내고 응답 받기
        
        Args:
            user_message: 사용자 메시지
            system_message: 시스템 메시지 (선택사항)
            temperature: 온도 (기본값: self.temperature)
            **kwargs: 추가 파라미터
            
        Returns:
            LLM 응답 텍스트
        """
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        messages.append(HumanMessage(content=user_message))
        
        logger.debug(f"LLM 호출: {user_message[:100]}...")
        
        try:
            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM 호출 실패: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        프롬프트에서 답변 생성 (invoke의 별칭)
        
        Args:
            prompt: 프롬프트
            system_context: 시스템 컨텍스트
            **kwargs: 추가 파라미터
            
        Returns:
            생성된 텍스트
        """
        return self.invoke(prompt, system_message=system_context, **kwargs)
    
    def parse_json(
        self,
        text: str,
        schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        텍스트에서 JSON 파싱
        
        Args:
            text: 파싱할 텍스트
            schema: 예상 스키마 (선택사항)
            **kwargs: 추가 파라미터
            
        Returns:
            파싱된 JSON 객체
        """
        import json
        
        logger.debug("JSON 파싱 시도...")
        
        try:
            # 마크다운 코드 블록 제거
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {str(e)}")
            return {}


# 싱글톤 인스턴스
_llm_client: Optional[LLMClient] = None


def get_llm_client(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    force_new: bool = False
) -> LLMClient:
    """
    LLMClient 싱글톤 인스턴스 반환
    
    Args:
        model: 모델명
        temperature: 온도
        force_new: 새로운 인스턴스 생성 강제
        
    Returns:
        LLMClient 인스턴스
    """
    global _llm_client
    
    if _llm_client is None or force_new:
        _llm_client = LLMClient(model=model, temperature=temperature)
    
    return _llm_client

