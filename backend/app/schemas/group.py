from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional


class WechatGroup(BaseModel):
    """微信群"""
    id: int
    group_name: str
    group_id: str
    member_count: int = 0
    is_active: bool = True
    inquiry_notify: bool = True
    quote_notify: bool = True
    delivery_notify: bool = True
    deal_notify: bool = True
    work_start_time: Optional[time] = None
    work_end_time: Optional[time] = None
    notify_keywords: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WechatGroupCreate(BaseModel):
    """创建微信群"""
    group_name: str = Field(..., min_length=1, max_length=200)
    group_id: str = Field(..., min_length=1, max_length=100)
    member_count: int = 0
    is_active: bool = True


class WechatGroupUpdate(BaseModel):
    """更新微信群"""
    group_name: Optional[str] = Field(None, max_length=200)
    member_count: Optional[int] = None
    is_active: Optional[bool] = None
    inquiry_notify: Optional[bool] = None
    quote_notify: Optional[bool] = None
    delivery_notify: Optional[bool] = None
    deal_notify: Optional[bool] = None
    work_start_time: Optional[time] = None
    work_end_time: Optional[time] = None
    notify_keywords: Optional[str] = None
