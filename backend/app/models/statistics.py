"""
statistics模型模块
定义statistics表结构
"""

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Text
from app.models.base import BaseModel


class Statistics(BaseModel):
    """数据统计表 - 车架号识别统计"""
    __tablename__ = "statistics"
    __table_args__ = {"comment": "统计表 - 存储VIN查询统计"}

    # 基本信息
    date = Column(DateTime, nullable=False, comment="日期")

    # 识别信息
    recognize_status = Column(String(20), nullable=False, comment="识别状态：success/fail")
    vin_code = Column(String(50), nullable=True, comment="车架号")
    car_model = Column(String(200), nullable=True, comment="车型")

    # 来源信息
    source_group = Column(String(200), nullable=True, comment="来源群")
    inquirer = Column(String(100), nullable=True, comment="询价人")
    quoter = Column(String(100), nullable=True, comment="报价人")

    # 报价信息
    is_quoted = Column(Boolean, default=False, nullable=False, comment="是否报价")
    quote_time = Column(Integer, nullable=True, comment="报价时效（分钟）")
    supplier = Column(String(200), nullable=True, comment="汽配商")
