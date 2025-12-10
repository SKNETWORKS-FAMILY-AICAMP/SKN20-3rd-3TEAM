"""
하이브리드 검색 모듈
벡터 검색(Chroma) + 키워드 검색(BM25) 결합
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever


class EnsembleRetriever:
    """앙상블 리트리버: 여러 retriever 결과를 가중치 기반으로 결합"""
    
    def __init__(self, retrievers: List, weights: List[float]):
        """
        Args:
            retrievers: 리트리버 리스트
            weights: 각 리트리버의 가중치 리스트
        """
        self.retrievers = retrievers
        self.weights = weights
    
    def invoke(self, query: str) -> List[Document]:
        """
        여러 retriever의 결과를 가중치 기반으로 결합
        
        Args:
            query: 검색 쿼리
            
        Returns:
            결합된 Document 리스트
        """
        doc_scores = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            
            # 각 문서에 가중치 적용
            for i, doc in enumerate(docs):
                doc_id = hash(doc.page_content)
                # 순위 기반 스코어 (상위일수록 높은 점수)
                score = weight * (len(docs) - i) / len(docs)
                
                if doc_id in doc_scores:
                    doc_scores[doc_id]['score'] += score
                else:
                    doc_scores[doc_id] = {'doc': doc, 'score': score}
        
        # 스코어 기준으로 정렬
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
        return [item['doc'] for item in sorted_docs]


class HybridRetriever:
    """하이브리드 검색: 벡터 검색 + BM25 검색"""
    
    def __init__(self, vectorstore_manager, documents: List[Document] = None):
        """
        Args:
            vectorstore_manager: VectorStoreManager 인스턴스
            documents: BM25용 문서 리스트 (None이면 BM25 비활성화)
        """
        self.vectorstore_manager = vectorstore_manager
        self.documents = documents
        self.ensemble_retriever = None
        
        # BM25 리트리버 초기화
        if documents:
            self.bm25_retriever = BM25Retriever.from_documents(documents)
            self.bm25_retriever.k = 5
            
            # 앙상블 리트리버 생성
            chroma_retriever = vectorstore_manager.get_retriever(k=5)
            self.ensemble_retriever = EnsembleRetriever(
                retrievers=[chroma_retriever, self.bm25_retriever],
                weights=[0.7, 0.3]  # Chroma 70%, BM25 30%
            )
            print("✓ 하이브리드 검색 활성화 (Chroma + BM25)")
        else:
            print("✓ 벡터 검색만 사용")
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        하이브리드 검색 수행
        
        Args:
            query: 검색 쿼리
            k: 검색할 문서 개수
            
        Returns:
            검색된 Document 리스트
        """
        if self.ensemble_retriever:
            # 하이브리드 검색
            results = self.ensemble_retriever.invoke(query)
            return results[:k]
        else:
            # 벡터 검색만
            return self.vectorstore_manager.similarity_search(query, k=k)
    
    def format_docs(self, docs: List[Document]) -> str:
        """
        문서를 프롬프트용 텍스트로 포맷팅
        
        Args:
            docs: Document 리스트
            
        Returns:
            포맷된 텍스트
        """
        formatted_docs = []
        
        for doc in docs:
            metadata = doc.metadata
            
            # 데이터 유형에 따라 출처 정보 구성
            if metadata.get("source_type") == "qa_data":
                source_info = f"상담기록 - {metadata.get('lifeCycle', '')}/{metadata.get('department', '')}/{metadata.get('disease', '')}"
            else:
                source_info = f"서적 - {metadata.get('title', '')}"
                if metadata.get('author'):
                    source_info += f" (저자: {metadata['author']})"
            
            formatted_doc = f"""<document>
<content>{doc.page_content}</content>
<source_info>{source_info}</source_info>
<data_type>{metadata.get('source_type', 'unknown')}</data_type>
</document>"""
            
            formatted_docs.append(formatted_doc)
        
        return "\n\n".join(formatted_docs)
