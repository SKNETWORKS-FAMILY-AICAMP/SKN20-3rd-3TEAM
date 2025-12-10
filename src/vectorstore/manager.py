"""
벡터스토어 관리 모듈
기존 vectorstore.py를 클래스 기반으로 리팩토링
"""

import os
import time
import warnings
from typing import List
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

warnings.filterwarnings("ignore")
load_dotenv()


class VectorStoreManager:
    """벡터스토어 생성 및 관리 클래스"""
    
    def __init__(
        self,
        collection_name: str = "pet_health_qa_system",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "text-embedding-3-small",
        batch_size: int = 500
    ):
        """
        Args:
            collection_name: Chroma 컬렉션 이름
            persist_directory: 벡터 DB 저장 경로
            embedding_model: OpenAI 임베딩 모델
            batch_size: 배치 처리 크기
        """
        if not os.environ.get('OPENAI_API_KEY'):
            raise ValueError('.env 파일에 OPENAI_API_KEY를 설정하세요')
            
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.batch_size = batch_size
        self.embedding_function = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore = None
        
        print(f"✓ VectorStoreManager 초기화 완료")
        print(f"  - 컬렉션: {collection_name}")
        print(f"  - 저장 경로: {persist_directory}")
        print(f"  - 배치 크기: {batch_size}")
    
    def create_vectorstore(self, documents: List[Document]) -> bool:
        """
        벡터스토어 생성
        
        Args:
            documents: Document 객체 리스트
            
        Returns:
            성공 여부
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 벡터스토어 생성 시작: {len(documents)}개 문서")
            print(f"{'='*60}\n")
            
            # 첫 번째 배치로 벡터스토어 생성
            first_batch = documents[:self.batch_size]
            
            self.vectorstore = Chroma.from_documents(
                documents=first_batch,
                embedding=self.embedding_function,
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
            )
            
            print(f"✓ 첫 번째 배치 완료: {len(first_batch)}개 문서")
            
            # 나머지 문서들을 배치로 추가
            remaining_docs = documents[self.batch_size:]
            total_batches = len(remaining_docs) // self.batch_size + \
                           (1 if len(remaining_docs) % self.batch_size > 0 else 0)
            
            for i in range(0, len(remaining_docs), self.batch_size):
                batch_num = i // self.batch_size + 2
                batch = remaining_docs[i:i + self.batch_size]
                
                print(f"배치 {batch_num}/{total_batches + 1} 처리 중... ({len(batch)}개 문서)")
                
                try:
                    self.vectorstore.add_documents(batch)
                    print(f"✓ 배치 {batch_num} 완료!")
                    time.sleep(1)  # API 제한 방지
                    
                except Exception as e:
                    print(f"⚠️ 배치 {batch_num} 에러: {e}")
                    # 더 작은 배치로 재시도
                    smaller_batches = [batch[j:j+20] for j in range(0, len(batch), 20)]
                    for small_batch in smaller_batches:
                        try:
                            self.vectorstore.add_documents(small_batch)
                            time.sleep(0.5)
                        except Exception as small_e:
                            print(f"⚠️ 소 배치 에러: {small_e}")
            
            print(f"\n{'='*60}")
            print(f"✅ 벡터스토어 생성 완료!")
            print(f"  - 저장 경로: {self.persist_directory}")
            print(f"  - 컬렉션명: {self.collection_name}")
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"\n❌ 벡터스토어 생성 실패: {e}")
            return False
    
    def load_vectorstore(self) -> bool:
        """
        기존 벡터스토어 로드
        
        Returns:
            성공 여부
        """
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✓ 벡터스토어 로드 성공: {self.collection_name}")
            return True
        except Exception as e:
            print(f"⚠️ 벡터스토어 로드 실패: {e}")
            return False
    
    def get_retriever(self, k: int = 5, search_type: str = "similarity"):
        """
        리트리버 반환
        
        Args:
            k: 검색할 문서 개수
            search_type: 검색 타입 ("similarity", "mmr", "similarity_score_threshold")
            
        Returns:
            Retriever 객체
        """
        if self.vectorstore is None:
            if not self.load_vectorstore():
                raise ValueError("벡터스토어를 로드할 수 없습니다")
        
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs={"k": k}
        )
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        유사도 검색
        
        Args:
            query: 검색 쿼리
            k: 검색할 문서 개수
            
        Returns:
            Document 리스트
        """
        if self.vectorstore is None:
            if not self.load_vectorstore():
                return []
        
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"⚠️ 검색 실패: {e}")
            return []


if __name__ == "__main__":
    # 테스트
    import pickle
    
    # 전처리된 문서 로드
    with open("chunked_docs.pkl", "rb") as f:
        docs = pickle.load(f)
    
    # 벡터스토어 생성
    manager = VectorStoreManager(batch_size=500)
    manager.create_vectorstore(docs)
