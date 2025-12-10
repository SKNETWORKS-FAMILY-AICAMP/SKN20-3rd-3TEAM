"""
RAG 파이프라인 통합 모듈
전체 워크플로우 오케스트레이션
"""

import os
import pickle
from typing import Optional, Tuple

from src.data.preprocessor import DataPreprocessor
from src.vectorstore.manager import VectorStoreManager
from src.retrieval.hybrid_retriever import HybridRetriever
from src.generation.llm_chain import LLMChain
from src.utils.helpers import format_documents


class RAGPipeline:
    """RAG 파이프라인 클래스"""
    
    def __init__(
        self,
        project_root: Optional[str] = None,
        vectorstore_path: str = "./chroma_db",
        chunked_docs_path: str = "./chunked_docs.pkl",
        use_cache: bool = True
    ):
        """
        Args:
            project_root: 프로젝트 루트 경로
            vectorstore_path: 벡터 DB 저장 경로
            chunked_docs_path: 청크된 문서 저장 경로
            use_cache: 캐시 사용 여부
        """
        if project_root is None:
            # 현재 파일 기준으로 프로젝트 루트 자동 감지
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(current_file))
        
        self.project_root = project_root
        self.vectorstore_path = vectorstore_path
        self.chunked_docs_path = chunked_docs_path
        self.use_cache = use_cache
        
        # 컴포넌트 초기화
        self.preprocessor = None
        self.vectorstore_manager = None
        self.hybrid_retriever = None
        self.llm_chain = None
        
        print(f"✓ RAG 파이프라인 초기화 (루트: {self.project_root})")
    
    def setup(self, force_rebuild: bool = False) -> None:
        """
        파이프라인 설정 (데이터 전처리 + 벡터 DB 생성)
        
        Args:
            force_rebuild: 강제 재구성 여부
        """
        print("\n=== RAG 파이프라인 설정 시작 ===\n")
        
        # 1. 데이터 전처리
        print("1️⃣ 데이터 전처리...")
        self.preprocessor = DataPreprocessor(project_root=self.project_root)
        
        # 캐시 확인
        if self.use_cache and not force_rebuild and os.path.exists(self.chunked_docs_path):
            print(f"✓ 캐시된 청크 문서 발견: {self.chunked_docs_path}")
            with open(self.chunked_docs_path, 'rb') as f:
                chunked_docs = pickle.load(f)
            print(f"✓ 로드 완료: {len(chunked_docs)}개 청크")
        else:
            print("→ 전체 데이터 전처리 실행...")
            chunked_docs = self.preprocessor.process_all_data()
            
            # 캐시 저장
            if self.use_cache:
                with open(self.chunked_docs_path, 'wb') as f:
                    pickle.dump(chunked_docs, f)
                print(f"✓ 청크 문서 저장: {self.chunked_docs_path}")
        
        # 2. 벡터 DB 생성/로드
        print("\n2️⃣ 벡터 DB 설정...")
        self.vectorstore_manager = VectorStoreManager(persist_directory=self.vectorstore_path)
        
        if self.use_cache and not force_rebuild and os.path.exists(self.vectorstore_path):
            print(f"✓ 기존 벡터 DB 발견: {self.vectorstore_path}")
            self.vectorstore_manager.load_vectorstore()
        else:
            print("→ 벡터 DB 생성 중...")
            self.vectorstore_manager.create_vectorstore(chunked_docs)
        
        # 3. 하이브리드 리트리버 초기화
        print("\n3️⃣ 하이브리드 리트리버 초기화 (MMR 50% + BM25 50%)...")
        chroma_retriever = self.vectorstore_manager.get_retriever(k=5, search_type="mmr")
        self.hybrid_retriever = HybridRetriever(
            documents=chunked_docs,
            chroma_retriever=chroma_retriever,
            chroma_weight=0.5,
            bm25_weight=0.5,
            k=5
        )
        
        # 4. LLM 체인 초기화
        print("\n4️⃣ LLM 체인 초기화...")
        self.llm_chain = LLMChain(model="gpt-4o-mini", temperature=0)
        
        print("\n=== RAG 파이프라인 설정 완료 ===\n")
    
    def query(
        self,
        question: str,
        use_rewrite: bool = True,
        return_sources: bool = False
    ) -> Tuple[str, Optional[list]]:
        """
        RAG 쿼리 실행
        
        Args:
            question: 사용자 질문
            use_rewrite: 쿼리 재작성 사용 여부
            return_sources: 출처 문서 반환 여부
            
        Returns:
            (응답, 출처 문서 리스트 또는 None)
        """
        if not all([self.hybrid_retriever, self.llm_chain]):
            raise RuntimeError("파이프라인이 설정되지 않았습니다. setup()을 먼저 호출하세요.")
        
        # 1. 쿼리 재작성 (선택적)
        search_query = question
        if use_rewrite:
            search_query = self.llm_chain.rewrite_query(question)
        
        # 2. 문서 검색
        retrieved_docs = self.hybrid_retriever.search(search_query)
        print(f"✓ 검색된 문서: {len(retrieved_docs)}개")
        
        # 3. 컨텍스트 포매팅
        context = format_documents(retrieved_docs)
        
        # 4. 응답 생성
        response = self.llm_chain.generate_response(question, context)
        
        if return_sources:
            return response, retrieved_docs
        else:
            return response, None
    
    def interactive_query(self):
        """대화형 쿼리 모드"""
        print("\n=== 대화형 쿼리 모드 ===")
        print("질문을 입력하세요 (종료: 'quit' 또는 'exit')\n")
        
        while True:
            try:
                question = input("질문: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("종료합니다.")
                    break
                
                if not question:
                    continue
                
                print("\n검색 중...")
                response, sources = self.query(question, return_sources=True)
                
                print("\n" + "="*80)
                print(response)
                print("="*80 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n종료합니다.")
                break
            except Exception as e:
                print(f"\n⚠️ 오류 발생: {e}\n")


def main():
    """메인 실행 함수"""
    import sys
    
    # 프로젝트 루트를 sys.path에 추가
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 파이프라인 초기화 및 설정
    pipeline = RAGPipeline(project_root=project_root)
    
    # 설정 메뉴
    print("\n[설정 옵션]")
    print("1. 캐시 사용 (빠름)")
    print("2. 전체 재구성 (느림)")
    choice = input("선택 (1/2, 기본값: 1): ").strip() or "1"
    
    force_rebuild = (choice == "2")
    pipeline.setup(force_rebuild=force_rebuild)
    
    # 대화형 쿼리 시작
    pipeline.interactive_query()


if __name__ == "__main__":
    main()
