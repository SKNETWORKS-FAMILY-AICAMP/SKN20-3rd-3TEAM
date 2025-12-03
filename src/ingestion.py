"""
데이터 Ingestion 모듈
JSON 파일 로드 및 필드 추출
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document


def load_json_files(data_dir: str) -> List[Dict[str, Any]]:
    """
    지정된 디렉토리에서 모든 JSON 파일을 로드
    
    Args:
        data_dir: JSON 파일이 있는 디렉토리 경로
        
    Returns:
        JSON 데이터 리스트
    """
    json_files = []
    data_path = Path(data_dir)
    
    # 모든 JSON 파일 찾기
    for json_file in data_path.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 파일 경로 정보 추가
                data['_source_path'] = str(json_file)
                data['_file_name'] = json_file.name
                json_files.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            continue
    
    return json_files


def extract_text_from_json(json_data: Dict[str, Any]) -> str:
    """
    JSON 데이터에서 텍스트 필드 추출
    PDF/MD/TXT 파일이 포함된 경우도 처리
    
    Args:
        json_data: JSON 데이터 딕셔너리
        
    Returns:
        추출된 텍스트 문자열
    """
    text_parts = []
    
    # 주요 필드 추출
    fields_to_extract = ['disease', 'title', 'content', 'author', 'department', 'publisher']
    
    for field in fields_to_extract:
        if field in json_data and json_data[field]:
            value = json_data[field]
            if isinstance(value, str):
                # PDF/MD/TXT 파일 경로인지 확인 (간단한 체크)
                if value.endswith(('.pdf', '.md', '.txt')) and os.path.exists(value):
                    # 파일이 존재하면 읽기 시도
                    try:
                        if value.endswith('.txt'):
                            with open(value, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            text_parts.append(f"{field} (from file): {file_content}")
                        elif value.endswith('.md'):
                            with open(value, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            text_parts.append(f"{field} (from file): {file_content}")
                        elif value.endswith('.pdf'):
                            # PDF 처리는 PyPDFLoader 등이 필요하지만 여기서는 경로만 기록
                            text_parts.append(f"{field}: [PDF file: {value}]")
                    except Exception as e:
                        print(f"Warning: Could not read file {value}: {e}")
                        text_parts.append(f"{field}: {value}")
                else:
                    text_parts.append(f"{field}: {value}")
            elif isinstance(value, (dict, list)):
                text_parts.append(f"{field}: {json.dumps(value, ensure_ascii=False)}")
    
    # 나머지 필드도 텍스트로 변환
    for key, value in json_data.items():
        if key not in fields_to_extract and not key.startswith('_'):
            if isinstance(value, str) and value.strip():
                # 파일 경로 체크
                if value.endswith(('.pdf', '.md', '.txt')) and os.path.exists(value):
                    try:
                        if value.endswith(('.txt', '.md')):
                            with open(value, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            text_parts.append(f"{key} (from file): {file_content}")
                        elif value.endswith('.pdf'):
                            text_parts.append(f"{key}: [PDF file: {value}]")
                    except Exception as e:
                        print(f"Warning: Could not read file {value}: {e}")
                        text_parts.append(f"{key}: {value}")
                else:
                    text_parts.append(f"{key}: {value}")
            elif isinstance(value, (dict, list)):
                text_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    
    return "\n\n".join(text_parts)


def create_documents_from_json(json_files: List[Dict[str, Any]]) -> List[Document]:
    """
    JSON 파일들을 LangChain Document 객체로 변환
    
    Args:
        json_files: JSON 데이터 리스트
        
    Returns:
        Document 객체 리스트
    """
    documents = []
    
    for json_data in json_files:
        # 텍스트 추출
        content = extract_text_from_json(json_data)
        
        if not content.strip():
            continue
        
        # 메타데이터 구성
        metadata = {
            'source_path': json_data.get('_source_path', 'unknown'),
            'file_name': json_data.get('_file_name', 'unknown'),
            'department': json_data.get('department', 'unknown'),
            'title': json_data.get('title', 'unknown'),
            'author': json_data.get('author', 'unknown'),
        }
        
        # Document 생성
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        documents.append(doc)
    
    return documents


def ingest_data(data_dir: str) -> List[Document]:
    """
    데이터 디렉토리에서 JSON 파일들을 로드하고 Document로 변환
    
    Args:
        data_dir: 데이터 디렉토리 경로
        
    Returns:
        Document 객체 리스트
    """
    print(f"Loading JSON files from: {data_dir}")
    json_files = load_json_files(data_dir)
    print(f"Loaded {len(json_files)} JSON files")
    
    documents = create_documents_from_json(json_files)
    print(f"Created {len(documents)} documents")
    
    return documents


if __name__ == "__main__":
    # 테스트
    data_dir = "../data/Training/01.원천데이터"
    docs = ingest_data(data_dir)
    print(f"\nFirst document preview:")
    print(f"Content length: {len(docs[0].page_content)}")
    print(f"Metadata: {docs[0].metadata}")

