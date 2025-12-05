"""
로깅 유틸리티
"""
import logging
from typing import Optional


_loggers = {}


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    로거 인스턴스 반환
    
    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        로거 인스턴스
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        
        if level:
            logger.setLevel(level.upper())
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        _loggers[name] = logger
    
    return _loggers[name]

