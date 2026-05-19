from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class MemberType(BaseModel):
    """成员类型"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberTypeCreate(BaseModel):
    """创建成员类型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class Supplier(BaseModel):
    """汽配商"""
    id: int
    wxid: str
    name: str
    member_type_id: Optional[int] = None
    member_type: Optional[MemberType] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    """创建汽配商"""
    wxid: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    member_type_id: Optional[int] = None


class CarModel(BaseModel):
    """车型"""
    id: int
    name: str
    brand: Optional[str] = None
    series: Optional[str] = None
    displacement: Optional[str] = None
    year: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CarModelCreate(BaseModel):
    """创建车型"""
    name: str = Field(..., min_length=1, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    series: Optional[str] = Field(None, max_length=100)
    displacement: Optional[str] = Field(None, max_length=50)
    year: Optional[str] = Field(None, max_length=20)
