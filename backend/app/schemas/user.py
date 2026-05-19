from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础信息"""
    nickname: str = Field(..., min_length=2, max_length=50)
    username: str = Field(..., min_length=4, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^(1[3-9]\d{9})?$')
    email: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = Field(None, max_length=200)


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6, max_length=20)
    is_active: bool = True


class UserUpdate(BaseModel):
    """更新用户"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^(1[3-9]\d{9})?$')
    email: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    is_superuser: bool
    wx_id: Optional[str] = None
    wx_group_name: Optional[str] = None
    group_member_wxid: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    """用户列表"""
    list: list[UserResponse]
    total: int
    page: int
    page_size: int
