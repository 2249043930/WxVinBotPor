from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class BaseSchema(BaseModel):
    """基础Schema"""
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseSchema):
    """分页参数"""
    page: int = 1
    page_size: int = 20


class PaginationResponse(BaseSchema):
    """分页响应"""
    total: int
    page: int
    page_size: int
    total_pages: int


class ResponseModel(BaseSchema, Generic[T]):
    """统一响应模型"""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
