"""
데이터 전처리 및 청킹 모듈
기존 data preprocessing.py를 클래스 기반으로 리팩토링
"""

import os
import json
import glob
import warnings
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

warnings.filterwarnings("ignore")


class DataPreprocessor:
    """데이터 전처리 및 청킹 클래스"""
    
    def __init__(self, base_data_path: str = None, project_root: str = None):
        """
        Args:
            base_data_path: 데이터 기본 경로 (None이면 프로젝트 루트 기준)
            project_root: 프로젝트 루트 경로 (하위 호환성을 위해 유지)
        """
        if base_data_path is None:
            # project_root가 주어진 경우 사용, 아니면 자동 감지
            if project_root is not None:
                current_dir = project_root
            else:
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.base_path = os.path.join(current_dir, "1.데이터", "Training", "02.라벨링데이터")
        else:
            self.base_path = base_data_path
            
        # 청킹 전략 설정
        self.splitters = {
            "medical_data": RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                separators=['\n\n', '\n', '.', '!', '?', ',', ' ', '']
            ),
            "qa_data": RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=50,
                separators=['\n\nA:', 'Q:', '\n\n', '\n', '.', ' ', '']
            )
        }
        
    def load_medical_data(self, paths: List[str]) -> List[Document]:
        """
        의학지식 데이터 로드 (말뭉치)
        
        Args:
            paths: 말뭉치 데이터 폴더 경로 리스트
            
        Returns:
            Document 객체 리스트
        """
        docs = []
        
        for path in paths:
            if not os.path.exists(path):
                print(f"⚠️ 경로가 존재하지 않습니다: {path}")
                continue
                
            print(f"처리 중: {path}")
            
            for file_path in glob.glob(os.path.join(path, "**", "*.json"), recursive=True):
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        data = json.load(f)
                    
                    disease = data.get("disease", "") or ""
                    
                    meta = {
                        "title": data.get("title", ""),
                        "author": data.get("author", None),
                        "publisher": data.get("publisher", None),
                        "department": data.get("department", None),
                        "source_type": "medical_data",
                        "source_path": path,
                    }
                    
                    docs.append(Document(page_content=disease, metadata=meta))
                except Exception as e:
                    print(f"파일 처리 오류 ({file_path}): {e}")
                    continue
        
        print(f"✓ 총 {len(docs)}개 의학 문서 로드 완료")
        return docs
    
    def load_qa_data(self, paths: List[str]) -> List[Document]:
        """
        질의응답 데이터 로드
        
        Args:
            paths: QA 데이터 폴더 경로 리스트
            
        Returns:
            Document 객체 리스트
        """
        docs_qa = []
        
        for path_qa in paths:
            if not os.path.exists(path_qa):
                print(f"⚠️ 경로가 존재하지 않습니다: {path_qa}")
                continue
                
            print(f"처리 중: {path_qa}")
            
            for file_path in glob.glob(os.path.join(path_qa, "**", "*.json"), recursive=True):
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        data = json.load(f)
                    
                    meta_info = data.get("meta", {})
                    qa_info = data.get("qa", {})
                    
                    question = qa_info.get("input", "")
                    answer = qa_info.get("output", "")
                    
                    page_content = f"Q: {question}\n\nA: {answer}"
                    
                    metadata = {
                        "lifeCycle": meta_info.get("lifeCycle", ""),
                        "department": meta_info.get("department", ""),
                        "disease": meta_info.get("disease", ""),
                        "question": question,
                        "answer": answer,
                        "source_type": "qa_data",
                        "source_path": path_qa
                    }
                    
                    docs_qa.append(Document(page_content=page_content, metadata=metadata))
                except Exception as e:
                    print(f"파일 처리 오류 ({file_path}): {e}")
                    continue
        
        print(f"✓ 총 {len(docs_qa)}개 QA 문서 로드 완료")
        return docs_qa
    
    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        """
        문서 청킹
        
        Args:
            docs: Document 객체 리스트
            
        Returns:
            청킹된 Document 객체 리스트
        """
        chunked_docs = []
        
        print(f"\n청킹 시작: {len(docs)}개 문서")
        
        for doc in docs:
            source_type = doc.metadata.get("source_type", "")
            
            if source_type == "medical_data":
                splitter = self.splitters["medical_data"]
            elif source_type == "qa_data":
                splitter = self.splitters["qa_data"]
            else:
                continue
            
            chunks = splitter.split_documents([doc])
            
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_method": source_type
                })
            
            chunked_docs.extend(chunks)
        
        print(f"✓ 청킹 완료: {len(chunked_docs)}개 청크 생성\n")
        return chunked_docs
    
    def process_all_data(self) -> List[Document]:
        """
        전체 데이터 처리 파이프라인
        
        Returns:
            청킹된 Document 리스트
        """
        print("\n" + "="*60)
        print("🚀 데이터 전처리 시작")
        print("="*60)
        
        # QA 데이터 경로
        qa_paths = [
            os.path.join(self.base_path, "TL_질의응답데이터_내과"),
            os.path.join(self.base_path, "TL_질의응답데이터_안과"),
            os.path.join(self.base_path, "TL_질의응답데이터_외과"),
            os.path.join(self.base_path, "TL_질의응답데이터_치과"),
            os.path.join(self.base_path, "TL_질의응답데이터_피부과"),
        ]
        
        # 데이터 로드
        print("\n📄 QA 데이터 로드...")
        docs = self.load_qa_data(qa_paths)
        
        # 청킹
        print("\n✂️ 문서 청킹...")
        chunked_docs = self.chunk_documents(docs)
        
        print("\n" + "="*60)
        print(f"✅ 전처리 완료: 총 {len(chunked_docs)}개 청크")
        print("="*60 + "\n")
        
        return chunked_docs


if __name__ == "__main__":
    # 테스트
    preprocessor = DataPreprocessor()
    docs = preprocessor.process_all_data()
    
    # 결과 저장
    import pickle
    with open("chunked_docs.pkl", "wb") as f:
        pickle.dump(docs, f)
    print("✓ chunked_docs.pkl 저장 완료")
