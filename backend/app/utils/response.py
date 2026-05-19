from typing import Any, Optional


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error_response(message: str = "error", code: int = 1, data: Optional[Any] = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }
