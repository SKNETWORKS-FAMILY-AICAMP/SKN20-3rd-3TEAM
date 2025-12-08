"""
Data Processor Module
문서 전처리 및 청킹 처리

역할:
  - 다양한 형식의 문서 로딩 (PDF, TXT, JSON 등)
  - 텍스트 전처리 및 정규화
  - 문서 청킹 (고정 크기 또는 의미 기반)
  - 메타데이터 추출 및 관리
"""

import os
import json
import glob
from typing import List, Dict, Optional, Tuple
import re
import warnings
warnings.filterwarnings("ignore")

from langchain_core.documents import Document
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_medical_data(paths: List[str]) -> List[Document]:
    """
    의학지식 데이터 로드 (말뭉치 데이터)
    
    Args:
        paths: 말뭉치 데이터 폴더 경로 리스트
        
    Returns:
        List[Document]: Document 객체 리스트
    """
    docs = []
    
    for path in paths:
        print(f"처리 중인 경로: {path}")
        
        for file_path in glob.glob(os.path.join(path, "**", "*.json"), recursive=True):
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                
                disease = data.get("disease", "") or ""
                
                # 문서 내용: 질병 정보
                page_content = disease
                
                # 메타데이터 구성
                meta = {
                    "title": data.get("title", ""),
                    "author": data.get("author", None),
                    "publisher": data.get("publisher", None),
                    "department": data.get("department", None),
                    "source_type": "medical_data",
                    "source_path": path,
                }
                
                docs.append(Document(page_content=page_content, metadata=meta))
            except Exception as e:
                print(f"파일 처리 오류 ({file_path}): {e}")
                continue
    
    print(f"총 {len(docs)}개 의학 문서를 로드했습니다.")
    return docs


def load_qa_data(paths: List[str]) -> List[Document]:
    """
    질의응답 데이터 로드
    
    Args:
        paths: 질의응답 데이터 폴더 경로 리스트
        
    Returns:
        List[Document]: Document 객체 리스트
    """
    docs_qa = []
    
    for path_qa in paths:
        print(f"처리 중인 경로: {path_qa}")
        
        for file_path in glob.glob(os.path.join(path_qa, "**", "*.json"), recursive=True):
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                
                # meta와 qa 추출
                meta_info = data.get("meta", {})
                qa_info = data.get("qa", {})
                
                # page_content: 질문 + 답변을 하나로 합치기
                question = qa_info.get("input", "")
                answer = qa_info.get("output", "")
                
                # Q&A 형태로 구성 (검색 시 더 효과적)
                page_content = f"Q: {question}\n\nA: {answer}"
                
                # metadata: 메타정보 + QA 관련 정보
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
    
    print(f"총 {len(docs_qa)}개 QA 문서를 로드했습니다.")
    return docs_qa


def preprocess_document(file_path: str) -> List[str]:
    """
    파일을 로드하여 전처리하고 청크로 분할
    
    Args:
        file_path (str): 문서 파일 경로 (예: "data/disease/disease_001.json")
        
    Returns:
        List[str]: 전처리된 청크 리스트
    """
    # 단일 파일 처리는 batch_preprocess_documents를 통해 처리
    results = batch_preprocess_documents([file_path])
    if results:
        return [chunk.page_content for chunk in results]
    return []


def clean_text(text: str) -> str:
    """
    텍스트 정규화 및 정제
    
    Args:
        text (str): 원본 텍스트
        
    Returns:
        str: 정제된 텍스트
        
    처리:
        - 여러 개의 공백 제거 → 단일 공백
        - 특수문자 정규화
        - 불필요한 라인 브레이크 제거
        - HTML 태그 제거 (if present)
        - 인코딩 정상화 (UTF-8)
    
    TODO:
        - 정규식 기반 전처리 로직 구현
        - 언어별 불용어 제거 (선택)
    """
    # TODO: 정규식 기반 전처리
    # - re.sub(r'\s+', ' ', text)  # 여러 공백 → 단일 공백
    # - re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
    
    cleaned = text.strip()
    print(f"✓ [clean_text] 텍스트 정제 완료: {len(text)} → {len(cleaned)} 문자")
    return cleaned


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    텍스트를 의미 있는 크기로 분할
    
    Args:
        text (str): 분할할 텍스트
        chunk_size (int): 각 청크의 최대 문자 수 (기본값: 500)
        overlap (int): 청크 간 겹치는 문자 수 (기본값: 50)
        
    Returns:
        List[str]: 분할된 청크 리스트
        
    청킹 전략:
        1. Fixed-Size Chunking (고정 크기):
           - 텍스트를 일정 크기로 분할
           - 간단하지만 의미 경계 무시 가능
        
        2. Semantic Chunking (의미 기반):
           - 문장/문단 단위로 분할
           - 더 나음 (향후 구현)
        
    예시:
        텍스트: "문장1. 문장2. 문장3. ..."
        chunk_size=20, overlap=5
        
        결과:
        ["문장1. 문장2", "장2. 문장3", ...]
    
    TODO:
        - 고정 크기 청킹 알고리즘 구현
        - 의미 기반 청킹 (문장/문단 단위) 추가 구현
        - 빈 청크 필터링
    """
    # TODO: 청킹 로직
    # - 텍스트를 chunk_size 단위로 분할
    # - overlap만큼 겹치도록 조정
    
    # 더미 데이터
    num_chunks = (len(text) // (chunk_size - overlap)) + 1
    chunks = [f"[청크 {i}] {text[i*(chunk_size-overlap):i*(chunk_size-overlap)+chunk_size]}"
              for i in range(max(1, num_chunks))]
    
    print(f"✓ [chunk_text] {len(text)} 문자 → {len(chunks)}개 청크 생성")
    return chunks


def extract_metadata(file_path: str, text: str) -> Dict[str, str]:
    """
    문서의 메타데이터 추출
    
    Args:
        file_path (str): 문서 파일 경로
        text (str): 문서 텍스트
        
    Returns:
        Dict[str, str]: 메타데이터 딕셔너리
            {
                'source': '파일 경로',
                'title': '문서 제목',
                'date_created': '생성 날짜',
                'content_length': '텍스트 길이',
                'language': '언어'
            }
    
    TODO:
        - 파일 시스템에서 메타데이터 추출
        - 문서 내 제목 추출 (정규식 또는 NLP)
        - 언어 감지
    """
    # TODO: 메타데이터 추출 로직
    
    metadata = {
        'source': file_path,
        'title': file_path.split('/')[-1].split('.')[0],
        'content_length': len(text),
        'language': 'ko'
    }
    
    print(f"✓ [extract_metadata] 메타데이터 추출 완료: {metadata}")
    return metadata


def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    문서들을 청킹 처리
    
    Args:
        docs: Document 객체 리스트
        
    Returns:
        List[Document]: 청킹된 Document 객체 리스트
    """
    # 데이터 타입별 splitter 정의
    splitter_map = {
        # 의학 데이터 (긴 설명문)
        "medical_data": RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=['\n\n', '\n', '.', '!', '?', ',', ' ', '']
        ),
        
        # QA 데이터 (질문-답변 쌍)
        "qa_data": RecursiveCharacterTextSplitter(
            chunk_size=800,  # QA는 더 큰 청크로
            chunk_overlap=50,
            separators=['\n\nA:', 'Q:', '\n\n', '\n', '.', ' ', '']
        )
    }
    
    # 기본 splitter (매칭되지 않는 경우)
    default_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=['\n\n', '\n', '.', ',', ' ', '']
    )
    
    chunked_docs = []
    
    print(f"\n청킹 대상 원본 Document 수: {len(docs)}개")
    
    # 각 문서의 source_type에 따라 다른 splitter 적용
    for doc in docs:
        source_type = doc.metadata.get("source_type", "")
        
        # 데이터 타입에 맞는 splitter 선택
        if source_type == "medical_data":
            splitter = splitter_map["medical_data"]
        elif source_type == "qa_data":
            splitter = splitter_map["qa_data"]
        else:
            splitter = default_splitter
        
        # 청킹 실행
        chunks = splitter.split_documents([doc])
        
        # 청킹된 문서들에 원본 메타데이터 보존 + 청킹 정보 추가
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_method": source_type
            })
        
        chunked_docs.extend(chunks)
    
    print(f"최종 청킹 결과: {len(chunked_docs)}개 Document")
    return chunked_docs


def batch_preprocess_documents(
    file_paths: List[str],
    chunk_size: int = 500
) -> List[Document]:
    """
    여러 문서를 배치로 전처리
    
    Args:
        file_paths (List[str]): 처리할 파일 경로 리스트 (폴더 경로)
        chunk_size (int): 청크 크기
        
    Returns:
        List[Document]: 청킹된 Document 객체 리스트
    """
    print(f"\n🔄 [batch_preprocess_documents] 배치 처리 시작\n")
    
    # 의학 데이터 경로와 QA 데이터 경로 분리
    medical_paths = [p for p in file_paths if "말뭉치" in p or "medical" in p.lower()]
    qa_paths = [p for p in file_paths if "질의응답" in p or "qa" in p.lower()]
    
    # 1. 의학지식 데이터 로드
    print("\n" + "=" * 30)
    print("의학지식 데이터 로드 및 전처리")
    print("=" * 30)
    
    docs = []
    if medical_paths:
        docs = load_medical_data(medical_paths)
        if docs:
            print(f"샘플 의학 문서:\n{docs[0].page_content[:300]}")
            print(f"메타데이터: {docs[0].metadata}")
    
    # 2. 질의응답 데이터 로드
    print("\n" + "=" * 30)
    print("질의응답 데이터 로드 및 전처리")
    print("=" * 30)
    
    if qa_paths:
        docs_qa = load_qa_data(qa_paths)
        if docs_qa:
            print(f"샘플 QA 문서:\n{docs_qa[0].page_content[:300]}")
            print(f"메타데이터: {docs_qa[0].metadata}")
            docs.extend(docs_qa)
    
    print(f"\n최종 문서 개수: {len(docs)}개")
    
    # 3. 청킹
    print("\n" + "=" * 30)
    print("문서 청킹 처리")
    print("=" * 30)
    
    chunked_docs = chunk_documents(docs)
    
    print(f"\n✅ 배치 처리 완료: 총 {len(chunked_docs)}개 청크 생성\n")
    return chunked_docs


# ==================== 엔트리 포인트 ====================
if __name__ == "__main__":
    """
    테스트 실행 (스켈레톤 데모)
    """
    
    print("\n" + "="*60)
    print("📄 Data Processor Module - 테스트")
    print("="*60 + "\n")
    
    # 테스트 1: 단일 문서 전처리
    print("### 테스트 1: 단일 문서 전처리 ###\n")
    test_file = "data/disease/disease_001.json"
    chunks = preprocess_document(test_file)
    print(f"✓ {len(chunks)}개 청크 생성\n")
    
    # 테스트 2: 텍스트 정규화
    print("### 테스트 2: 텍스트 정규화 ###\n")
    sample_text = "  여러    공백이   있는    텍스트  입니다.  "
    cleaned = clean_text(sample_text)
    print(f"원본: '{sample_text}'")
    print(f"정제: '{cleaned}'\n")
    
    # 테스트 3: 배치 처리
    print("### 테스트 3: 배치 처리 ###\n")
    test_files = [
        "data/disease/disease_001.json",
        "data/disease/disease_002.json"
    ]
    batch_results = batch_preprocess_documents(test_files)
    
    print("="*60)
    print("✅ 테스트 완료!")
    print("="*60)

