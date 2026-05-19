from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LogRecord(BaseModel):
    """日志记录"""
    id: int
    user_id: Optional[int] = None
    nickname: Optional[str] = None
    ip_address: Optional[str] = None
    login_location: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    login_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class LogList(BaseModel):
    """日志列表"""
    list: list[LogRecord]
    total: int
    page: int
    page_size: int


class OperationLogRecord(BaseModel):
    """操作日志记录"""
    id: int
    nickname: Optional[str] = None
    ip_address: Optional[str] = None
    login_location: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    login_time: datetime
    operation: Optional[str] = None
    operation_type: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
