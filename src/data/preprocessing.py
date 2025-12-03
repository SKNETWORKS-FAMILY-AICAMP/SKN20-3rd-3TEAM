"""
데이터 로드 및 전처리 모듈
반려동물 질환 데이터를 로드하고 RAG 파이프라인을 위한 Document 객체로 변환
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 최적화 모듈 import
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.optimization import (
        preprocess_text_with_stopwords,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
        KOREAN_SEPARATORS
    )
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    print("⚠️ 최적화 모듈을 불러올 수 없습니다. 기본 전처리만 사용합니다.")
    OPTIMIZATION_AVAILABLE = False
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    KOREAN_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def clean_text(text: str, remove_stopwords: bool = False) -> str:
    """
    텍스트 정제: 불필요한 공백, 특수문자 제거
    
    Args:
        text: 원본 텍스트
        remove_stopwords: True면 불용어 제거 수행
        
    Returns:
        정제된 텍스트
    """
    if not text:
        return ""
    
    # 연속된 공백을 하나로 통합
    text = re.sub(r'\s+', ' ', text)
    
    # 특수 제어 문자 제거
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # 불용어 제거 (옵션)
    if remove_stopwords and OPTIMIZATION_AVAILABLE:
        text = preprocess_text_with_stopwords(text)
    
    return text


def _remove_boilerplate_text(text: str) -> str:
    """
    답변에서 정형화된 관리 지침 문구 제거 (지침 4.2: 후처리)
    
    Args:
        text: 원본 답변 텍스트
        
    Returns:
        정형화 문구가 제거된 텍스트
    """
    # 반복적으로 등장하는 정형화 문구 패턴
    boilerplate_patterns = [
        r'날짜를 함께 적어 비교해\s*주세요[.。]*',
        r'기록을 남겨\s*주세요[.。]*',
        r'수의사와\s*상담.*권장.*',
        r'반려동물.*건강.*기원.*'
    ]
    
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    JSON 파일 로드
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        파싱된 JSON 딕셔너리
    """
    try:
        # UTF-8 BOM 처리를 위해 utf-8-sig 사용
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def load_and_preprocess_data(
    file_path: str,
    chunk_size: int = None,  # None이면 최적화된 값 사용
    chunk_overlap: int = None,  # None이면 최적화된 값 사용
    data_type: str = "source",  # "source" 또는 "labeled"
    remove_stopwords: bool = False  # 불용어 제거 여부
) -> List[Document]:
    """
    원천 데이터(또는 라벨링 데이터)를 로드하고 LangChain Document 객체로 변환
    
    Args:
        file_path: JSON 파일 또는 디렉토리 경로
        chunk_size: 청크 크기 (토큰 수 기준)
        chunk_overlap: 청크 오버랩 크기
        data_type: "source" (원천 데이터) 또는 "labeled" (라벨링 데이터)
        
    Returns:
        LangChain Document 객체 리스트
    """
    documents = []
    
    # 최적화된 청크 설정 적용
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = CHUNK_OVERLAP
    
    print(f"📐 청크 설정: size={chunk_size}, overlap={chunk_overlap}")
    if remove_stopwords:
        print(f"🗑️ 불용어 제거: 활성화")
    
    # 텍스트 분할기 초기화 (최적화된 구분자 사용)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=KOREAN_SEPARATORS if OPTIMIZATION_AVAILABLE else ["\n\n", "\n", ". ", " ", ""]
    )
    
    # 파일 경로 처리
    path = Path(file_path)
    
    if path.is_file():
        files_to_process = [path]
    elif path.is_dir():
        files_to_process = list(path.glob("*.json"))
    else:
        print(f"Invalid path: {file_path}")
        return documents
    
    # 각 JSON 파일 처리
    for file in files_to_process:
        data = load_json_file(str(file))
        
        if not data:
            continue
        
        if data_type == "source":
            # 원천 데이터 처리 (TS_말뭉치데이터)
            documents.extend(_process_source_data(data, text_splitter, str(file), remove_stopwords))
        elif data_type == "labeled":
            # 라벨링 데이터 처리 (TL_질의응답데이터)
            documents.extend(_process_labeled_data(data, text_splitter, str(file), remove_stopwords))
    
    print(f"총 {len(documents)}개의 Document 청크가 생성되었습니다.")
    return documents


def _process_source_data(
    data: Dict[str, Any],
    text_splitter: RecursiveCharacterTextSplitter,
    file_path: str,
    remove_stopwords: bool = False
) -> List[Document]:
    """
    원천 데이터(TS_말뭉치데이터) 처리
    
    구조:
    {
        "title": "소동물 주요 질환의 임상추론...",
        "author": "현창백 내과아카데미 역",
        "publisher": "(주)범문에듀케이션",
        "department": "내과",
        "disease": "황달 증례의 임상적 추론... (긴 텍스트)"
    }
    """
    documents = []
    
    # disease 필드 추출 및 정제
    disease_text = data.get("disease", "")
    if not disease_text:
        return documents
    
    disease_text = clean_text(disease_text, remove_stopwords=remove_stopwords)
    
    # 응급도 키워드 감지 (지침 5: 응급도 판단 정확도 개선)
    urgency_level = _detect_urgency_from_text(disease_text)
    
    # 메타데이터 구성 (지침 4.1: department를 metadata에 포함)
    metadata = {
        "title": data.get("title", ""),
        "author": data.get("author", ""),
        "publisher": data.get("publisher", ""),
        "department": data.get("department", ""),  # 필터링용
        "source_file": file_path,
        "data_type": "source",
        "urgency": urgency_level  # 응급 키워드 기반 응급도
    }
    
    # 텍스트 청크 분할
    chunks = text_splitter.split_text(disease_text)
    
    # 각 청크를 Document 객체로 변환
    for i, chunk in enumerate(chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_id"] = i
        chunk_metadata["total_chunks"] = len(chunks)
        
        doc = Document(
            page_content=chunk,
            metadata=chunk_metadata
        )
        documents.append(doc)
    
    return documents


def _detect_urgency_from_text(text: str) -> str:
    """
    텍스트에서 응급 키워드를 감지하여 응급도 추정
    
    Args:
        text: 질환 설명 텍스트
        
    Returns:
        'High', 'Medium', 'Low'
    """
    text_lower = text.lower()
    
    # 고위험 키워드
    high_urgency_keywords = [
        '발작', '경련', '의식', '호흡곤란', '청색증', '쇼크', '출혈', 
        '응급', '즉시', '급성', '중독', '비틀림', '팽만', '탈수',
        '저혈당', '고열', '파열', '폐색', '질식'
    ]
    
    # 중위험 키워드
    medium_urgency_keywords = [
        '구토', '설사', '기침', '감염', '염증', '통증', '발열',
        '부종', '궤양', '출혈', '외상', '골절'
    ]
    
    # 키워드 매칭
    for keyword in high_urgency_keywords:
        if keyword in text_lower or keyword in text:
            return 'High'
    
    for keyword in medium_urgency_keywords:
        if keyword in text_lower or keyword in text:
            return 'Medium'
    
    return 'Low'


def _process_labeled_data(
    data: Dict[str, Any],
    text_splitter: RecursiveCharacterTextSplitter,
    file_path: str,
    remove_stopwords: bool = False
) -> List[Document]:
    """
    라벨링 데이터(TL_질의응답데이터) 처리
    
    구조:
    {
        "meta": {"lifeCycle": "자견", "department": "내과", "disease": "기타"},
        "qa": {
            "instruction": "너는 반려견 건강 전문가야...",
            "input": "저희 집 강아지가 구토를 하고...",
            "output": "질문 내용을 확인하였습니다..."
        }
    }
    """
    documents = []
    
    meta = data.get("meta", {})
    qa = data.get("qa", {})
    
    if not qa:
        return documents
    
    # 답변에서 정형화된 관리 지침 문구 제거 (지침 4.2: 후처리)
    output_text = clean_text(qa.get('output', ''), remove_stopwords=remove_stopwords)
    output_text = _remove_boilerplate_text(output_text)
    
    # QA 쌍을 하나의 컨텍스트로 결합
    qa_text = f"""질문: {clean_text(qa.get('input', ''), remove_stopwords=remove_stopwords)}

답변: {output_text}"""
    
    # 메타데이터 구성 (지침 4.2: lifeCycle, instruction 포함)
    metadata = {
        "life_cycle": meta.get("lifeCycle", ""),  # 질문 속성 부여용
        "department": meta.get("department", ""),  # 필터링용
        "disease": meta.get("disease", ""),
        "instruction": qa.get("instruction", ""),  # System Prompt 참고용
        "source_file": file_path,
        "data_type": "labeled"
    }
    
    # 텍스트 청크 분할 (QA는 보통 짧으므로 하나의 청크로 처리될 가능성 높음)
    chunks = text_splitter.split_text(qa_text)
    
    # 각 청크를 Document 객체로 변환
    for i, chunk in enumerate(chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_id"] = i
        chunk_metadata["total_chunks"] = len(chunks)
        
        doc = Document(
            page_content=chunk,
            metadata=chunk_metadata
        )
        documents.append(doc)
    
    return documents


def load_multiple_departments(
    base_path: str,
    departments: List[str] = ["내과", "외과", "안과", "치과", "피부과"],
    data_type: str = "source",
    chunk_size: int = None,  # None이면 최적화된 값 사용
    chunk_overlap: int = None,  # None이면 최적화된 값 사용
    remove_stopwords: bool = False  # 불용어 제거 여부
) -> List[Document]:
    """
    여러 진료과 데이터를 일괄 로드
    
    Args:
        base_path: 데이터 기본 경로
        departments: 로드할 진료과 리스트
        data_type: "source" 또는 "labeled"
        chunk_size: 청크 크기
        chunk_overlap: 청크 오버랩
        
    Returns:
        모든 진료과의 Document 리스트
    """
    all_documents = []
    
    for dept in departments:
        if data_type == "source":
            dept_path = os.path.join(base_path, f"TS_말뭉치데이터_{dept}")
        else:
            dept_path = os.path.join(base_path, f"TL_질의응답데이터_{dept}")
        
        if os.path.exists(dept_path):
            print(f"\n{dept} 데이터 로드 중...")
            docs = load_and_preprocess_data(
                dept_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                data_type=data_type,
                remove_stopwords=remove_stopwords
            )
            all_documents.extend(docs)
        else:
            print(f"경로를 찾을 수 없습니다: {dept_path}")
    
    return all_documents


# 예제 사용법
if __name__ == "__main__":
    # 원천 데이터 로드 예제
    source_data_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training\01.원천데이터\TS_말뭉치데이터_내과"
    
    print("=== 원천 데이터 로드 ===")
    source_docs = load_and_preprocess_data(
        source_data_path,
        chunk_size=1000,
        chunk_overlap=200,
        data_type="source"
    )
    
    if source_docs:
        print(f"\n첫 번째 Document 샘플:")
        print(f"내용: {source_docs[0].page_content[:200]}...")
        print(f"메타데이터: {source_docs[0].metadata}")
    
    # 라벨링 데이터 로드 예제
    labeled_data_path = r"c:\LDG_CODES\SKN20\3rd_prj\data\59.반려견 성장 및 질병 관련 말뭉치 데이터\3.개방데이터\1.데이터\Training\02.라벨링데이터\TL_질의응답데이터_내과"
    
    print("\n\n=== 라벨링 데이터 로드 ===")
    labeled_docs = load_and_preprocess_data(
        labeled_data_path,
        chunk_size=1000,
        chunk_overlap=200,
        data_type="labeled"
    )
    
    if labeled_docs:
        print(f"\n첫 번째 Document 샘플:")
        print(f"내용: {labeled_docs[0].page_content[:200]}...")
        print(f"메타데이터: {labeled_docs[0].metadata}")
