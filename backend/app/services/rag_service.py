"""
RAG Service - 기존 prompt_module.py 로직을 서비스로 분리
"""
import os
import warnings
warnings.filterwarnings("ignore")

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings

# 기존 코드 임포트 (상대 경로 조정)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from ensemble import EnsembleRetriever

from ..core.config import settings


class RAGService:
    """RAG 시스템 서비스"""
    
    def __init__(self):
        self.vectorstore = None
        self.llm = None
        self.retriever_similarity = None
        self.retriever_bm25 = None
        self.retriever_ensemble = None
        self.embeddings = None
        
    def initialize(self):
        """RAG 시스템 초기화"""
        print("RAG 시스템 초기화 중...")
        
        # 임베딩 모델 로드
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={'device': settings.EMBEDDING_DEVICE},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 벡터스토어 로드
        vectorstore_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../', settings.VECTORSTORE_PATH)
        )
        
        self.vectorstore = Chroma(
            persist_directory=vectorstore_path,
            collection_name=settings.COLLECTION_NAME,
            embedding_function=self.embeddings
        )
        print(f"벡터스토어 로드 완료: {vectorstore_path}")
        
        # LLM 초기화
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        
        # Retrievers 생성
        self._create_retrievers()
        
        print("RAG 시스템 초기화 완료!")
        
    def _create_retrievers(self, k=5):
        """모든 retriever 생성"""
        # Similarity retriever
        self.retriever_similarity = self.vectorstore.as_retriever(
            search_kwargs={"k": k},
            search_type="similarity"
        )
        
        # BM25 retriever
        collection = self.vectorstore._collection
        doc_count = collection.count()
        
        if doc_count > 0:
            all_data = collection.get(limit=doc_count)
            bm25_docs = []
            
            if all_data and 'ids' in all_data and len(all_data['ids']) > 0:
                documents = all_data.get('documents', [])
                metadatas = all_data.get('metadatas', [])
                
                for i, doc_id in enumerate(all_data['ids']):
                    page_content = documents[i] if i < len(documents) else ""
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    bm25_docs.append(Document(page_content=page_content, metadata=metadata))
            
            self.retriever_bm25 = BM25Retriever.from_documents(bm25_docs)
            self.retriever_bm25.k = k
            
            # Ensemble retriever
            self.retriever_ensemble = EnsembleRetriever(
                retrievers=[self.retriever_similarity, self.retriever_bm25],
                weights=[0.5, 0.5]
            )
            
    def get_retriever(self, search_type: str = "ensemble", k: int = 5):
        """검색 타입에 따라 retriever 반환"""
        # k값이 변경되면 retriever 재생성
        if self.retriever_similarity is None or \
           getattr(self.retriever_similarity, 'search_kwargs', {}).get('k') != k:
            self._create_retrievers(k)
        
        if search_type == "similarity":
            return self.retriever_similarity
        elif search_type == "bm25":
            return self.retriever_bm25
        else:  # ensemble
            return self.retriever_ensemble
    
    def get_rag_prompt(self) -> ChatPromptTemplate:
        """RAG 답변 생성 프롬프트"""
        return ChatPromptTemplate.from_messages([
            ("system", """
당신은 반려견 질병·증상에 대해 수의학 정보를 제공하는 AI 어시스턴트입니다. 
당신의 답변은 반드시 제공된 문맥(Context)만을 기반으로 해야 합니다.
문맥에 없는 정보는 절대로 추측하거나 생성하지 마세요.

[사용 가능한 정보 유형]
- medical_data: 수의학 서적 또는 논문
- qa_data: 보호자-수의사 상담 기록 (생애주기 / 과 / 질병 태그 포함)

[할루시네이션 방지 규칙]
1. 일반적인 상식과 상이하게 다른 터무니없는 질문에 대해서는 "해당 질문과 관련된 문서를 찾지 못했습니다."라고 답변하세요.
2. 문맥에 없는 정보는 사용하지 마세요.
3. 관련 정보가 없다면 "해당 질문과 관련된 문서를 찾지 못했습니다."라고 답변하세요.
4. 여러 문서 제공시, 실제로 답변에 사용한 문서만 출처 명시하세요.
5. 사용자가 견종이나 나이를 특정해서 언급하지 않는 이상 응답에는 견종이나 나이를 절대 포함하지 않아야 합니다.

[응답 규칙]
- 보호자가 작성한 질문을 간단히 요약한다.
- 문맥에서 확인된 가능한 원인을 구체적으로 설명한다.
- 집에서 가능한 안전한 관리 방법 2~3개 제안한다.
- 병원 방문이 필요한 경우와 응급 증상을 명확히 안내한다.
- 사용한 정보의 출처를 명시한다 (서적명/저자 또는 상담기록 태그).

Context:
{context}

Question: {question}
Answer:"""),
        ])
    
    def get_rewrite_prompt(self) -> PromptTemplate:
        """Query Rewriting 프롬프트"""
        return PromptTemplate(
            template="""당신은 사용자 질문을 검색에 최적화된 키워드로 변환하는 전문가입니다.

원본 질문: {question}

위 질문을 아래 규칙에 따라 핵심 검색 키워드로 변환하세요:
1. 불필요한 조사, 어미 제거
2. 핵심 증상/질병명만 추출
3. 의학 용어로 변환 (예: "토해요" → "구토")
4. 간결하게 3~5개 단어로 축약

변환된 검색어:""",
            input_variables=["question"]
        )
    
    def format_docs(self, docs: List[Document]) -> str:
        """문서를 컨텍스트 문자열로 포맷"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            source_type = meta.get('source_type', 'unknown')
            
            if source_type == 'qa_data':
                lifecycle = meta.get('lifeCycle', '')
                dept = meta.get('department', '')
                disease = meta.get('disease', '')
                label = f"[{lifecycle}/{dept}/{disease}]" if any([lifecycle, dept, disease]) else ""
                formatted.append(f"문서 {i} {label}:\n{doc.page_content}\n")
            else:
                title = meta.get('title', '')
                author = meta.get('author', '')
                citation = f"({title}, {author})" if title or author else ""
                formatted.append(f"문서 {i} {citation}:\n{doc.page_content}\n")
        
        return "\n".join(formatted)
    
    async def chat(
        self,
        question: str,
        search_type: str = "ensemble",
        k: int = 5,
        use_rewrite: bool = False
    ) -> Dict[str, Any]:
        """채팅 처리"""
        try:
            # Query Rewriting
            rewritten_query = None
            if use_rewrite:
                rewrite_chain = self.get_rewrite_prompt() | self.llm | StrOutputParser()
                rewritten_query = rewrite_chain.invoke({"question": question})
                search_query = rewritten_query
            else:
                search_query = question
            
            # 문서 검색
            retriever = self.get_retriever(search_type, k)
            docs = retriever.invoke(search_query)
            
            # RAG 답변 생성
            prompt = self.get_rag_prompt()
            rag_chain = prompt | self.llm | StrOutputParser()
            
            answer = rag_chain.invoke({
                "context": self.format_docs(docs),
                "question": question
            })
            
            # 문서 정보 변환
            sources = []
            for doc in docs:
                sources.append({
                    "content": doc.page_content[:500],  # 길이 제한
                    "metadata": doc.metadata,
                    "source_type": doc.metadata.get("source_type", "unknown")
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "search_type": search_type,
                "rewritten_query": rewritten_query
            }
            
        except Exception as e:
            raise Exception(f"채팅 처리 중 오류: {str(e)}")
    
    async def search_documents(
        self,
        query: str,
        search_type: str = "ensemble",
        k: int = 5
    ) -> Dict[str, Any]:
        """문서 검색만 수행"""
        try:
            retriever = self.get_retriever(search_type, k)
            docs = retriever.invoke(query)
            
            documents = []
            for doc in docs:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source_type": doc.metadata.get("source_type", "unknown")
                })
            
            return {
                "documents": documents,
                "search_type": search_type,
                "total_count": len(documents)
            }
            
        except Exception as e:
            raise Exception(f"문서 검색 중 오류: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """서비스 상태 확인"""
        try:
            chromadb_status = "ok" if self.vectorstore else "not initialized"
            model_loaded = self.llm is not None
            
            vectorstore_count = None
            if self.vectorstore:
                try:
                    vectorstore_count = self.vectorstore._collection.count()
                except:
                    vectorstore_count = -1
            
            return {
                "status": "healthy",
                "chromadb_status": chromadb_status,
                "model_loaded": model_loaded,
                "vectorstore_count": vectorstore_count
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "chromadb_status": "error",
                "model_loaded": False,
                "vectorstore_count": None,
                "error": str(e)
            }


# 전역 인스턴스
rag_service = RAGService()
