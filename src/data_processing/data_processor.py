"""
Data Processor Module
문서 전처리 및 청킹 처리

역할:
  - 다양한 형식의 문서 로딩 (PDF, TXT, JSON 등)
  - 텍스트 전처리 및 정규화
  - 문서 청킹 (고정 크기 또는 의미 기반)
  - 메타데이터 추출 및 관리
"""

from typing import List, Dict, Optional, Tuple
import re


def preprocess_document(file_path: str) -> List[str]:
    """
    파일을 로드하여 전처리하고 청크로 분할
    
    Args:
        file_path (str): 문서 파일 경로 (예: "data/disease/disease_001.json")
        
    Returns:
        List[str]: 전처리된 청크 리스트
            각 청크는 의미 있는 단위로 분할된 텍스트
            예: ["청크1 텍스트...", "청크2 텍스트...", ...]
        
    처리 순서:
        1️⃣  [파일 로드] 파일 형식 감지 및 로드 (JSON/TXT/PDF)
        2️⃣  [텍스트 추출] JSON → dict → 필드별 텍스트 추출
        3️⃣  [전처리] 불필요한 공백/특수문자 정규화
        4️⃣  [청킹] 의미 단위로 문서 분할 (chunk_size=500, overlap=50)
        5️⃣  [검증] 빈 청크 제거, 최소 길이 확인
        
    예시:
        입력: "data/disease/disease_001.json"
        
        파일 내용:
        {
            "disease_name": "강아지 피부염",
            "symptoms": "가려움증, 털 손실",
            "treatment": "약물 치료..."
        }
        
        출력:
        [
            "강아지 피부염 증상: 가려움증, 털 손실",
            "강아지 피부염 치료 방법: 약물 치료..."
        ]
    
    TODO:
        - 파일 형식별 로더 구현 (load_json, load_txt, load_pdf)
        - 텍스트 정규화 함수 구현
        - 의미 기반 청킹 또는 고정 크기 청킹 구현
        - 메타데이터 추출 (제목, 출처 등)
    """
    # 파일 형식 감지
    file_ext = file_path.split('.')[-1].lower()
    
    # 더미 데이터: 전처리된 청크 리스트 반환
    chunks = [
        f"[청크 1] 문서: {file_path}\n문서 내용 청크 1: 의료 정보 관련 텍스트...",
        f"[청크 2] 문서: {file_path}\n문서 내용 청크 2: 치료 방법 관련 텍스트..."
    ]
    
    print(f"📄 [preprocess_document] {file_path} 처리 완료 → {len(chunks)}개 청크 생성")
    return chunks


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


def batch_preprocess_documents(
    file_paths: List[str],
    chunk_size: int = 500
) -> List[Dict[str, any]]:
    """
    여러 문서를 배치로 전처리
    
    Args:
        file_paths (List[str]): 처리할 파일 경로 리스트
        chunk_size (int): 청크 크기
        
    Returns:
        List[Dict[str, any]]: 각 문서별 처리 결과
            [
                {
                    'file_path': 'path/to/file',
                    'chunks': ['청크1', '청크2', ...],
                    'chunk_count': 2,
                    'metadata': {...}
                },
                ...
            ]
    
    TODO:
        - 배치 처리 로직
        - 에러 처리 (파일 없음 등)
        - 진행률 표시
    """
    # TODO: 배치 처리 로직
    
    results = []
    
    print(f"\n🔄 [batch_preprocess_documents] {len(file_paths)}개 파일 배치 처리 시작\n")
    
    for idx, file_path in enumerate(file_paths, 1):
        print(f"  [{idx}/{len(file_paths)}] 처리 중: {file_path}")
        
        # 각 파일 처리
        chunks = preprocess_document(file_path)
        
        # 메타데이터 추출
        text = '\n'.join(chunks)
        metadata = extract_metadata(file_path, text)
        
        result = {
            'file_path': file_path,
            'chunks': chunks,
            'chunk_count': len(chunks),
            'metadata': metadata
        }
        
        results.append(result)
    
    print(f"\n✅ 배치 처리 완료: 총 {sum(r['chunk_count'] for r in results)}개 청크 생성\n")
    return results


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

