"""
공통 유틸리티 함수
=================
프로젝트 전체에서 사용할 수 있는 도우미 함수들
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import hashlib

from .config import LoggingConfig, Constants


# ============ 로깅 설정 ============
def setup_logging(config: Optional[LoggingConfig] = None) -> logging.Logger:
    """
    로깅 설정
    
    Args:
        config: 로깅 설정 객체
        
    Returns:
        로거 인스턴스
    """
    config = config or LoggingConfig()
    
    # 로그 디렉토리 생성
    log_dir = Path(config.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 로거 설정
    logger = logging.getLogger("RAG_Pipeline")
    logger.setLevel(getattr(logging, config.level))
    
    # 파일 핸들러
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        config.log_file,
        maxBytes=config.max_file_size,
        backupCount=config.backup_count
    )
    file_handler.setFormatter(logging.Formatter(config.format))
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.format))
    logger.addHandler(console_handler)
    
    return logger


# ============ 파일 I/O 유틸리티 ============
def load_json(file_path: str) -> Dict[str, Any]:
    """
    JSON 파일 로드
    
    Args:
        file_path: 파일 경로
        
    Returns:
        파싱된 JSON 데이터
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"JSON 형식이 잘못되었습니다: {file_path}")


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2):
    """
    JSON 파일 저장
    
    Args:
        data: 저장할 데이터
        file_path: 파일 경로
        indent: 들여쓰기 크기
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """
    JSONL 파일 로드 (한 줄에 하나의 JSON 객체)
    
    Args:
        file_path: 파일 경로
        
    Returns:
        JSON 객체 리스트
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 형식이 잘못되었습니다: {file_path} - {e}")


def save_jsonl(data: List[Dict[str, Any]], file_path: str):
    """
    JSONL 파일 저장
    
    Args:
        data: 저장할 데이터 리스트
        file_path: 파일 경로
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


# ============ 텍스트 처리 유틸리티 ============
def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 256) -> List[str]:
    """
    텍스트를 청크로 분할
    
    Args:
        text: 분할할 텍스트
        chunk_size: 청크 크기
        overlap: 청크 겹침 크기
        
    Returns:
        청크 리스트
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    텍스트를 지정된 길이로 축약
    
    Args:
        text: 축약할 텍스트
        max_length: 최대 길이
        suffix: 뒤에 붙일 문자열
        
    Returns:
        축약된 텍스트
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """
    텍스트 정리 (공백, 특수문자 등)
    
    Args:
        text: 정리할 텍스트
        
    Returns:
        정리된 텍스트
    """
    # 연속된 공백을 하나의 공백으로
    import re
    text = re.sub(r'\s+', ' ', text)
    # 양 끝 공백 제거
    text = text.strip()
    return text


def split_sentences(text: str) -> List[str]:
    """
    텍스트를 문장 단위로 분할
    
    Args:
        text: 분할할 텍스트
        
    Returns:
        문장 리스트
    """
    import re
    # 마침표, 물음표, 느낌표를 기준으로 분할
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


# ============ 해시 유틸리티 ============
def hash_text(text: str, algorithm: str = 'md5') -> str:
    """
    텍스트의 해시값 생성
    
    Args:
        text: 해시할 텍스트
        algorithm: 해시 알고리즘 (md5, sha256)
        
    Returns:
        해시값
    """
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"지원하지 않는 알고리즘: {algorithm}")


def generate_id(prefix: str = "doc") -> str:
    """
    고유한 ID 생성
    
    Args:
        prefix: ID 접두사
        
    Returns:
        생성된 ID
    """
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ============ 시간 유틸리티 ============
def get_timestamp() -> str:
    """현재 타임스탬프 (ISO 형식)"""
    return datetime.now().isoformat()


def get_timestamp_millis() -> int:
    """현재 타임스탐프 (밀리초)"""
    import time
    return int(time.time() * 1000)


# ============ 검증 유틸리티 ============
def is_valid_query(query: str, min_length: int = 1, max_length: int = Constants.MAX_QUERY_LENGTH) -> bool:
    """
    쿼리 유효성 검사
    
    Args:
        query: 검사할 쿼리
        min_length: 최소 길이
        max_length: 최대 길이
        
    Returns:
        유효 여부
    """
    if not query or not isinstance(query, str):
        return False
    
    query = query.strip()
    return min_length <= len(query) <= max_length


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    API 키 유효성 검사
    
    Args:
        api_key: 검사할 API 키
        
    Returns:
        유효 여부
    """
    return api_key is not None and len(api_key) > 0


# ============ 통계 유틸리티 ============
def calculate_average(values: List[float]) -> float:
    """평균 계산"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_percentile(values: List[float], percentile: int = 50) -> float:
    """백분위수 계산"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[index]


# ============ 형식 변환 유틸리티 ============
def format_time(seconds: float) -> str:
    """
    시간을 읽기 쉬운 형식으로 변환
    
    Args:
        seconds: 초 단위 시간
        
    Returns:
        형식화된 시간 문자열
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = seconds / 60
        return f"{minutes:.2f}m"


def format_size(bytes_size: int) -> str:
    """
    파일 크기를 읽기 쉬운 형식으로 변환
    
    Args:
        bytes_size: 바이트 단위 크기
        
    Returns:
        형식화된 크기 문자열
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f}TB"


# ============ 환경 변수 유틸리티 ============
def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    환경 변수 조회
    
    Args:
        key: 환경 변수명
        default: 기본값
        required: 필수 여부
        
    Returns:
        환경 변수 값
        
    Raises:
        ValueError: required=True이고 환경 변수가 없는 경우
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"필수 환경 변수가 설정되지 않았습니다: {key}")
    return value


# ============ 캐싱 유틸리티 ============
def cache_result(func):
    """
    함수 결과 캐싱 데코레이터
    
    사용 예:
    @cache_result
    def expensive_function(arg):
        return result
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = hash_text(str(args) + str(kwargs))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    
    return wrapper


# ============ 리스트 유틸리티 ============
def remove_duplicates(items: List[str]) -> List[str]:
    """
    리스트에서 중복 제거 (순서 유지)
    
    Args:
        items: 원본 리스트
        
    Returns:
        중복 제거된 리스트
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    리스트를 배치로 분할
    
    Args:
        items: 원본 리스트
        batch_size: 배치 크기
        
    Returns:
        배치로 분할된 리스트
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


# ============ 딕셔너리 유틸리티 ============
def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    두 딕셔너리 병합
    
    Args:
        dict1: 첫 번째 딕셔너리
        dict2: 두 번째 딕셔너리 (우선)
        
    Returns:
        병합된 딕셔너리
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    딕셔너리에서 특정 키만 추출
    
    Args:
        data: 원본 딕셔너리
        keys: 추출할 키 리스트
        
    Returns:
        필터링된 딕셔너리
    """
    return {k: v for k, v in data.items() if k in keys}


