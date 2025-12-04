"""
공통 로깅 설정

모든 모듈에서 일관된 로깅을 수행하기 위한 logger를 설정합니다.
"""

import logging
import sys
from typing import Optional

from src.config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 생성 및 반환

    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 반환
    if logger.handlers:
        return logger

    # 로그 레벨 설정
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 포매터 설정
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# 전역 로거
logger = get_logger(__name__)

