"""
공통 헬퍼 함수 모듈

전체 시스템에서 사용되는 유틸리티 함수들을 정의합니다.
"""

import time
from typing import Any, Callable, TypeVar

from src.config.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def timer(func: Callable[..., T]) -> Callable[..., T]:
    """
    함수 실행 시간을 측정하고 로깅하는 데코레이터

    Args:
        func: 시간을 측정할 함수

    Returns:
        wrapper: 래핑된 함수
    """

    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} executed in {elapsed:.2f} seconds")
        return result

    return wrapper


def extract_keywords(text: str, keywords_list: list[str]) -> list[str]:
    """
    텍스트에서 주어진 키워드 목록을 추출합니다.

    Args:
        text: 검색할 텍스트
        keywords_list: 찾을 키워드 리스트

    Returns:
        list: 발견된 키워드 리스트
    """
    text_lower = text.lower()
    found_keywords = [
        keyword for keyword in keywords_list
        if keyword.lower() in text_lower
    ]
    return found_keywords


def normalize_text(text: str) -> str:
    """
    텍스트를 정규화합니다 (공백 정리, 소문자 변환 등)

    Args:
        text: 정규화할 텍스트

    Returns:
        str: 정규화된 텍스트
    """
    # 여러 공백을 하나로 통일
    normalized = " ".join(text.split())
    # 소문자 변환
    normalized = normalized.lower()
    return normalized


def calculate_relevance_score(doc_score: float, text_length: int) -> float:
    """
    문서의 관련성 점수를 계산합니다.

    Args:
        doc_score: 벡터 검색 점수 (0.0 ~ 1.0)
        text_length: 문서 길이

    Returns:
        float: 최종 관련성 점수 (0.0 ~ 1.0)

    Note:
        이 함수는 기본 구현이며, 팀에서 더 정교한 로직으로 확장 가능합니다.
    """
    # 길이가 너무 짧으면 점수 감소
    if text_length < 50:
        length_factor = 0.7
    elif text_length > 2000:
        length_factor = 0.9
    else:
        # 선형 보간
        length_factor = 0.7 + (text_length - 50) / (2000 - 50) * 0.2

    final_score = doc_score * length_factor
    return min(1.0, final_score)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    텍스트를 겹치는 청크로 분할합니다.

    Args:
        text: 분할할 텍스트
        chunk_size: 각 청크의 크기
        overlap: 청크 간 겹치는 부분의 크기

    Returns:
        list: 분할된 청크 리스트
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # 다음 시작점은 현재 끝에서 겹치는 부분을 뺀 곳
        start = end - overlap

    return chunks


def safe_dict_get(
    dictionary: dict[str, Any],
    key: str,
    default: Any = None,
    nested: bool = False,
) -> Any:
    """
    안전하게 딕셔너리 값을 가져옵니다.

    Args:
        dictionary: 검색할 딕셔너리
        key: 키 (nested=True일 때 "parent.child" 형식 지원)
        default: 기본값
        nested: 중첩 키 지원 여부

    Returns:
        Any: 찾은 값 또는 기본값
    """
    try:
        if nested and "." in key:
            keys = key.split(".")
            value = dictionary
            for k in keys:
                value = value[k]
            return value
        else:
            return dictionary.get(key, default)
    except (KeyError, TypeError):
        return default

