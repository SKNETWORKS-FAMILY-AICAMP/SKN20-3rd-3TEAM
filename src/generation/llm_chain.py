"""
LLM 체인 모듈
프롬프트 + LLM + 응답 생성
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


# RAG 프롬프트
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
문맥에 없는 정보는 절대로 추측하거나 생성하지 마세요.

[사용 가능한 정보 유형]
- medical_data: 수의학 서적 또는 논문
- qa_data: 보호자-수의사 상담 기록 (생애주기 / 과 / 질병 태그 포함)

[할루시네이션 방지 규칙]
1. 문맥에 없는 정보는 사용하지 마세요.
2. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."라고 답변하세요.
3. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
4. 질문에 합당한 답변만 제공하세요.

[응답 규칙]
- 보호자가 작성한 반려견 상태를 2~3문장으로 요약한다.
- 문맥에서 확인된 가능한 원인을 구체적으로 설명한다.
- 집에서 가능한 안전한 관리 방법 2~3개 제안한다.
- 언제 병원에 가야 하는지, 어떤 증상이 응급인지 문서 기반으로 설명한다.
- 마지막 줄에 반드시 출처를 명시한다:
  • 서적 출처: 책 제목 / 저자 / 출판사
  • QA 출처: 생애주기 / 과 / 질병

[전체 톤]
- 공손한 존댓말
- 보호자를 안심시키되, 필요한 부분은 명확하게 안내하는 수의사 상담 톤

[출력 형식]
상태 요약:
가능한 원인:
집에서 관리 방법:
병원 방문 시기:
출처(참고한 모든 문서):
"""),
    ("human", """
문맥: {context}

사용자 질문: {question}
""")
])


# 쿼리 재작성 프롬프트
REWRITE_PROMPT = PromptTemplate.from_template(
    """다음 질문을 검색에 더 적합한 형태로 변환해 주세요.
키워드 중심으로 명확하게 바꿔주세요.
변환된 검색어만 출력하세요.

원본 질문: {question}
변환된 검색어:"""
)


class LLMChain:
    """LLM 체인 클래스"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Args:
            model: 사용할 LLM 모델
            temperature: 생성 온도
        """
        if not os.environ.get('OPENAI_API_KEY'):
            raise ValueError('.env 파일에 OPENAI_API_KEY를 설정하세요')
            
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # 체인 생성
        self.rag_chain = RAG_PROMPT | self.llm | StrOutputParser()
        self.rewrite_chain = REWRITE_PROMPT | self.llm | StrOutputParser()
        
        print(f"✓ LLM 체인 초기화 완료 (모델: {model})")
    
    def rewrite_query(self, query: str) -> str:
        """
        쿼리를 검색에 최적화된 형태로 재작성
        
        Args:
            query: 원본 쿼리
            
        Returns:
            재작성된 쿼리
        """
        try:
            transformed = self.rewrite_chain.invoke({'question': query})
            print(f"✓ 쿼리 재작성: {query} → {transformed}")
            return transformed
        except Exception as e:
            print(f"⚠️ 쿼리 재작성 실패: {e}")
            return query
    
    def generate_response(self, query: str, context: str) -> str:
        """
        RAG 응답 생성
        
        Args:
            query: 사용자 쿼리
            context: 검색된 문서 컨텍스트
            
        Returns:
            생성된 응답
        """
        try:
            response = self.rag_chain.invoke({
                "context": context,
                "question": query
            })
            return response
        except Exception as e:
            print(f"⚠️ 응답 생성 실패: {e}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
