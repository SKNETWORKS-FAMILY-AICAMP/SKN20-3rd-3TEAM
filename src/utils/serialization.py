"""
직렬화 유틸리티
"""
from datetime import datetime
from typing import Any, Dict, List


def serialize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    결과를 JSON 직렬화 가능한 형태로 변환
    datetime 객체 등을 문자열로 변환
    
    Args:
        result: 변환할 결과 딕셔너리
        
    Returns:
        직렬화 가능한 딕셔너리
    """
    if isinstance(result, dict):
        serialized = {}
        for key, value in result.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_result(value)
            elif isinstance(value, list):
                serialized[key] = [
                    serialize_result(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    elif isinstance(result, list):
        return [serialize_result(item) if isinstance(item, dict) else item for item in result]
    
    elif isinstance(result, datetime):
        return result.isoformat()
    
    return result

