"""
RAG 파이프라인 구축 모듈 (LangChain 활용)
Vector Store 설정, Retriever 구성, RAG 체인 생성
"""

import os
import sys
from typing import List, Optional, Dict, Any

# 상위 디렉토리 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# 수의학 전문가 System Prompt 템플릿 (지침 4.2: instruction 기반)
VETERINARY_EXPERT_SYSTEM_PROMPT = """당신은 반려동물 건강 전문가이자 수의학 전문의입니다.
친절하고 전문가적인 어투로 답변하되, 최종 진단은 반드시 수의사에게 받아야 함을 항상 강조하세요.

## 당신의 역할
- 반려동물(주로 반려견)의 증상을 분석하고 의심 질환 정보를 제공합니다.
- 제공된 전문 수의학 지식 데이터베이스를 기반으로 신뢰도 높은 답변을 제공합니다.
- 응급 상황을 판단하고 필요시 즉시 병원 방문을 권장합니다.

## 답변 원칙 (지침 4.1: Citation 포함)
1. **근거 기반**: 반드시 제공된 컨텍스트(context)를 기반으로 답변하세요.
2. **출처 표기**: 답변 말미에 "※ 참고문헌: [검색된 문서의 title/author]"를 명시하세요.
3. **명확성**: 전문 용어를 사용할 때는 쉬운 설명을 덧붙이세요.
4. **안전 우선**: 불확실한 경우 또는 심각한 증상의 경우 반드시 수의사 방문을 권장하세요.
5. **구조화**: 답변은 다음 구조로 작성하세요.
   - 증상 요약
   - 의심 질환 (전문 용어 + 쉬운 설명)
   - 주의사항
   - 권장 조치
   - 참고문헌 (출처)

## 응급 상황 판단 기준 (지침 5: 응급도 키워드)
다음 증상이 있을 경우 **높은 응급도**로 판단하고 즉시 병원 방문을 권장하세요:
- 심한 호흡 곤란, 청색증, 질식
- 발작, 경련, 의식 저하
- 지속적인 구토나 설사 (특히 혈변)
- 심한 출혈, 쇼크
- 복부 팽만 및 극심한 통증 (위 비틀림 의심)
- 고체온 (40도 이상) 또는 저체온
- 급성 중독, 탈수

## 제공된 컨텍스트
{context}

## 사용자 질문
{input}

위 정보를 바탕으로 전문적이고 신뢰할 수 있는 답변을 제공해주세요."""


def setup_embeddings(
    model_name: str = "text-embedding-3-small",
    openai_api_key: Optional[str] = None
) -> OpenAIEmbeddings:
    """
    OpenAI 임베딩 모델 설정 (HuggingFace 대신 사용)
    
    Args:
        model_name: 사용할 임베딩 모델명 (text-embedding-ada-002 또는 text-embedding-3-small)
        openai_api_key: OpenAI API 키
        
    Returns:
        OpenAIEmbeddings 인스턴스
    """
    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    embeddings = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=openai_api_key
    )
    
    print(f"임베딩 모델 '{model_name}' 로드 완료")
    return embeddings


def setup_vector_store(
    documents: List[Document],
    embeddings: OpenAIEmbeddings,
    persist_directory: str = "./chroma_db",
    collection_name: str = "pet_health_knowledge"
) -> Chroma:
    """
    Chroma Vector Store 설정
    
    Args:
        documents: Document 객체 리스트
        embeddings: 임베딩 모델
        persist_directory: 벡터 DB 저장 경로
        collection_name: 컬렉션 이름
        
    Returns:
        Chroma 벡터 스토어 인스턴스
    """
    print(f"Vector Store 생성 중... (총 {len(documents)}개 문서)")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    print(f"Vector Store 생성 완료: {persist_directory}")
    return vectorstore


def load_existing_vector_store(
    embeddings: OpenAIEmbeddings,
    persist_directory: str = "./chroma_db",
    collection_name: str = "pet_health_knowledge"
) -> Optional[Chroma]:
    """
    기존 Vector Store 로드
    
    Args:
        embeddings: 임베딩 모델
        persist_directory: 벡터 DB 저장 경로
        collection_name: 컬렉션 이름
        
    Returns:
        Chroma 벡터 스토어 인스턴스 또는 None
    """
    if not os.path.exists(persist_directory):
        print(f"Vector Store가 존재하지 않습니다: {persist_directory}")
        return None
    
    try:
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        print(f"기존 Vector Store 로드 완료: {persist_directory}")
        return vectorstore
    except Exception as e:
        print(f"Vector Store 로드 실패: {e}")
        return None


def setup_rag_pipeline(
    documents: List[Document],
    embedding_model: str = "text-embedding-3-small",
    anthropic_api_key: Optional[str] = None,
    model_name: str = "gpt-4o-mini",
    persist_directory: str = "./chroma_db",
    use_existing_vectorstore: bool = False,
    k: int = 4,  # 검색할 문서 수
    filter_metadata: Optional[Dict[str, Any]] = None
):
    """
    RAG 파이프라인 설정 (Vector Store + Retriever + LLM Chain)
    
    Args:
        documents: Document 객체 리스트
        embedding_model: 임베딩 모델명
        anthropic_api_key: Anthropic API 키
        model_name: Claude 모델명
        persist_directory: Vector Store 저장 경로
        use_existing_vectorstore: 기존 Vector Store 사용 여부
        k: 검색할 문서 개수
        filter_metadata: 메타데이터 필터링 조건 (예: {"department": "내과"})
        
    Returns:
        RAG 체인 및 관련 컴포넌트를 포함한 딕셔너리
    """
    # 1. 임베딩 모델 설정
    embeddings = setup_embeddings(embedding_model)
    
    # 2. Vector Store 설정
    if use_existing_vectorstore:
        vectorstore = load_existing_vector_store(embeddings, persist_directory)
        if vectorstore is None:
            print("기존 Vector Store가 없으므로 새로 생성합니다.")
            vectorstore = setup_vector_store(documents, embeddings, persist_directory)
    else:
        vectorstore = setup_vector_store(documents, embeddings, persist_directory)
    
    # 3. Retriever 설정 (메타데이터 필터링 지원)
    search_kwargs = {"k": k}
    if filter_metadata:
        search_kwargs["filter"] = filter_metadata
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs
    )
    
    print(f"Retriever 설정 완료 (k={k}, filter={filter_metadata})")
    
    # 4. LLM 설정 (OpenAI)
    openai_api_key = anthropic_api_key if anthropic_api_key else os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    
    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=openai_api_key,
        temperature=0.3,  # 일관성 있는 답변을 위해 낮은 temperature
        max_tokens=2048
    )
    
    print(f"LLM 설정 완료: {model_name}")
    
    # 5. Prompt 템플릿 설정
    prompt = ChatPromptTemplate.from_template(VETERINARY_EXPERT_SYSTEM_PROMPT)
    
    # 6. RAG 체인 구성 (LCEL 방식) - 지침 4.1: Citation 포함
    def format_docs(docs):
        """검색된 문서를 포맷팅 (출처 정보 포함)"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            dept = doc.metadata.get('department', '알 수 없음')
            title = doc.metadata.get('title', '제목 없음')
            author = doc.metadata.get('author', '저자 미상')
            urgency = doc.metadata.get('urgency', 'Low')
            
            # 출처 정보와 함께 포맷팅
            doc_header = f"[문서 {i} - {dept}과 / 응급도: {urgency}]"
            doc_source = f"(출처: {title} - {author})"
            doc_content = doc.page_content
            
            formatted.append(f"{doc_header}\n{doc_content}\n{doc_source}\n")
        return "\n".join(formatted)
    
    rag_chain = (
        {
            "context": retriever | format_docs,
            "input": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("RAG 파이프라인 구성 완료")
    
    return {
        "chain": rag_chain,
        "retriever": retriever,
        "vectorstore": vectorstore,
        "llm": llm,
        "embeddings": embeddings
    }


def query_rag(rag_chain, query: str) -> str:
    """
    RAG 체인에 질의
    
    Args:
        rag_chain: RAG 체인 (LCEL 방식)
        query: 사용자 질문
        
    Returns:
        생성된 답변
    """
    try:
        response = rag_chain.invoke(query)
        return response
    except Exception as e:
        return f"오류 발생: {str(e)}"


# 예제 사용법
if __name__ == "__main__":
    from data.preprocessing import load_and_preprocess_data
    from dotenv import load_dotenv
    
    # 환경 변수 로드
    load_dotenv()
    
    # 샘플 데이터 로드 (실제 경로로 변경 필요)
    print("=== 데이터 로드 ===")
    source_data_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training\01.원천데이터\TS_말뭉치데이터_내과"
    
    documents = load_and_preprocess_data(
        source_data_path,
        chunk_size=1000,
        chunk_overlap=200,
        data_type="source"
    )
    
    if not documents:
        print("문서를 로드할 수 없습니다.")
        exit()
    
    # RAG 파이프라인 설정
    print("\n=== RAG 파이프라인 설정 ===")
    rag_components = setup_rag_pipeline(
        documents=documents,
        use_existing_vectorstore=False,
        k=4
    )
    
    # 테스트 쿼리
    print("\n=== 테스트 쿼리 ===")
    test_query = "저희 강아지가 구토를 계속하고 황달 증상이 있어요. 어떤 질환일까요?"
    
    answer = query_rag(rag_components["chain"], test_query)
    print(f"\n질문: {test_query}")
    print(f"\n답변:\n{answer}")
