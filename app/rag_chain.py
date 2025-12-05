"""
RAG 체인 정의 - 검색 및 LLM 응답 생성
"""
from typing import List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from app.config import settings, VECTOR_STORE_DIR


class RAGChain:
    """RAG 검색 및 응답 생성 체인"""

    def __init__(self):
        """RAG 체인 초기화"""

        # 임베딩 모델
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 벡터스토어 로드
        self.vectorstore = Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=self.embeddings,
            collection_name="dog_symptoms"
        )

        # LLM 초기화
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # 프롬프트 템플릿
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "{question}\n\n참고 자료:\n{context}")
        ])

    def _get_system_prompt(self) -> str:
        """시스템 프롬프트 반환"""
        return """당신은 강아지 건강 상담 전문 수의사 어시스턴트입니다.

당신의 역할:
1. 보호자가 설명하는 강아지의 증상을 듣고, 가능한 원인과 질병을 설명합니다.
2. 집에서 주의해야 할 점, 해도 되는 행동, 하면 안 되는 행동을 명확히 안내합니다.
3. 병원 방문이 필요한지 여부를 판단하여 명확하게 알려줍니다.
4. 응급 상황이 의심되면 "지체하지 말고 즉시 동물병원 또는 응급실로 연락하세요"라고 강하게 권고합니다.

응답 형식:
- 친절하고 이해하기 쉬운 한국어로 작성
- 전문 용어 사용 시 쉬운 설명 추가
- 보호자가 불안해하지 않도록 공감하는 톤 유지
- 단, 응급 상황에서는 명확하고 단호하게 표현

참고 자료를 바탕으로 정확한 정보를 제공하되, 자료에 없는 내용은 일반적인 수의학 지식을 활용하세요.
"""

    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """
        벡터스토어에서 관련 문서 검색

        Args:
            query: 검색 쿼리
            k: 검색할 문서 개수

        Returns:
            List[Document]: 검색된 문서 리스트
        """
        if k is None:
            k = settings.RETRIEVAL_TOP_K

        try:
            documents = self.vectorstore.similarity_search(query, k=k)
            return documents
        except Exception as e:
            print(f"문서 검색 중 오류: {e}")
            return []

    def generate_response(self, query: str, documents: List[Document]) -> str:
        """
        검색된 문서를 기반으로 LLM 응답 생성

        Args:
            query: 사용자 질문
            documents: 검색된 참고 문서

        Returns:
            str: 생성된 응답
        """
        # 문서 내용 결합
        context = "\n\n---\n\n".join([
            f"[자료 {i+1}]\n{doc.page_content}"
            for i, doc in enumerate(documents)
        ])

        if not context.strip():
            context = "관련 자료를 찾을 수 없습니다."

        # 프롬프트 생성
        messages = self.prompt_template.format_messages(
            question=query,
            context=context
        )

        # LLM 호출
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"LLM 응답 생성 중 오류: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해 주세요."

    def run(self, query: str) -> dict:
        """
        전체 RAG 파이프라인 실행

        Args:
            query: 사용자 질문

        Returns:
            dict: 응답 및 소스 문서 정보
        """
        # 1. 문서 검색
        documents = self.retrieve(query)

        # 2. 응답 생성
        response = self.generate_response(query, documents)

        # 3. 소스 정보 추출
        sources = [
            {
                "disease": doc.metadata.get("disease", "Unknown"),
                "symptom": doc.metadata.get("symptom", "Unknown")
            }
            for doc in documents
        ]

        return {
            "response": response,
            "sources": sources,
            "num_sources": len(documents)
        }


# 싱글톤 인스턴스
rag_chain = RAGChain()
