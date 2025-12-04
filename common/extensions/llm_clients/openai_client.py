"""
OpenAI LLM 클라이언트 구현
========================
OpenAI API를 사용한 LLM 클라이언트 실제 구현
"""

from typing import Dict, Any, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from common.base import BaseLLMClient
from common.config import ModelConfig

logger = logging.getLogger(__name__)


class GradeDocuments(BaseModel):
    """문서 관련성 평가 결과"""
    binary_score: str = Field(
        description="문서가 질문과 관련이 있으면 'yes', 없으면 'no'"
    )


class OpenAILLMClient(BaseLLMClient):
    """
    OpenAI API 기반 LLM 클라이언트
    
    기능:
    - 텍스트 생성
    - 구조화된 판정 (yes/no)
    - 다양한 프롬프트 템플릿 지원
    """
    
    def __init__(self,
                 model_name: str = "gpt-4o-mini",
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None,
                 api_key: Optional[str] = None,
                 **kwargs):
        """
        Args:
            model_name: OpenAI 모델 이름 (기본: gpt-4o-mini)
            temperature: 창의성 수준 (0~2)
            max_tokens: 최대 토큰 수
            api_key: OpenAI API 키 (없으면 환경변수에서 로드)
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)
        
        try:
            # OpenAI ChatOpenAI 초기화
            init_params = {
                "model": model_name,
                "temperature": temperature,
            }
            
            if max_tokens:
                init_params["max_tokens"] = max_tokens
            
            if api_key:
                init_params["api_key"] = api_key
            
            self.llm = ChatOpenAI(**init_params)
            
            # 평가용 LLM (항상 temperature=0)
            self.grader_llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=api_key
            )
            
            logger.info(f"✅ OpenAI LLM 클라이언트 초기화 완료: {model_name}")
        
        except Exception as e:
            logger.error(f"❌ OpenAI LLM 초기화 실패: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 프롬프트
            **kwargs: 추가 옵션
                - temperature: 이 호출의 온도 (기본: self.temperature)
                
        Returns:
            생성된 텍스트
        """
        try:
            # 온도 재정의 가능
            temperature = kwargs.get('temperature', self.temperature)
            
            # 동적 temperature 설정
            if temperature != self.temperature:
                llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=temperature,
                    max_tokens=self.max_tokens
                )
            else:
                llm = self.llm
            
            # LLM 호출
            response = llm.invoke(prompt)
            
            # 응답 추출
            if hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            logger.debug(f"🤖 LLM 생성 완료: {len(result)} 토큰")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ 생성 오류: {e}")
            raise
    
    def grade(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        구조화된 판정 (yes/no 등)
        
        Args:
            prompt: 프롬프트
            **kwargs: 추가 옵션
            
        Returns:
            판정 결과
            {
                'is_relevant': bool,
                'score': float,
            }
        """
        try:
            logger.debug("⚖️ LLM 평가 시작")
            
            # 구조화된 grader 설정
            structured_grader = self.grader_llm.with_structured_output(
                GradeDocuments
            )
            
            # LLM 호출
            response = structured_grader.invoke(prompt)
            
            # 결과 추출
            is_relevant = response.binary_score.lower() == 'yes'
            score = 1.0 if is_relevant else 0.0
            
            logger.debug(f"⚖️ 평가 완료: {is_relevant} (점수: {score})")
            
            return {
                'is_relevant': is_relevant,
                'score': score,
            }
        
        except Exception as e:
            logger.error(f"❌ 평가 오류: {e}")
            # 오류 발생 시 기본값 반환
            return {
                'is_relevant': True,
                'score': 0.5,
            }
    
    def chat_completion(self, messages: list, **kwargs) -> str:
        """
        채팅 형식의 완성
        
        Args:
            messages: 메시지 리스트 [{"role": "user", "content": "..."}, ...]
            **kwargs: 추가 옵션
            
        Returns:
            응답 텍스트
        """
        try:
            # ChatPromptTemplate 생성
            template = ChatPromptTemplate.from_messages(messages)
            
            # LLM 호출
            chain = template | self.llm
            response = chain.invoke({})
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        
        except Exception as e:
            logger.error(f"❌ 채팅 완성 오류: {e}")
            raise
    
    def create_chain(self, prompt_template: str, **kwargs):
        """
        프롬프트 템플릿과 LLM으로 체인 생성
        
        Args:
            prompt_template: 프롬프트 템플릿 문자열
            **kwargs: 템플릿 변수
            
        Returns:
            LLMChain
        """
        template = ChatPromptTemplate.from_template(prompt_template)
        return template | self.llm

