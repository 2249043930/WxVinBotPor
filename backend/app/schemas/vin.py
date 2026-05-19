from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class VinRecord(BaseModel):
    """车架号记录"""
    id: int
    date: datetime
    recognize_status: str
    vin_code: Optional[str] = None
    car_model: Optional[str] = None
    source_group: Optional[str] = None
    inquirer: Optional[str] = None
    quoter: Optional[str] = None
    is_quoted: bool = False
    quote_time: Optional[int] = None
    supplier: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VinRecordList(BaseModel):
    """车架号记录列表"""
    list: list[VinRecord]
    total: int
    page: int
    page_size: int


class VinRecordDetail(BaseModel):
    """车架号记录详情"""
    id: int
    date: datetime
    recognize_status: str
    vin_code: Optional[str] = None
    car_model: Optional[str] = None
    source_group: Optional[str] = None
    inquirer: Optional[str] = None
    quoter: Optional[str] = None
    is_quoted: bool = False
    quote_time: Optional[int] = None
    supplier: Optional[str] = None
    raw_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
