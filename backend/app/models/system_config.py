"""系统配置模型"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import BaseModel


class SystemConfig(BaseModel):
    """系统配置表"""
    __tablename__ = "system_configs"
    __table_args__ = {"comment": "系统配置表 - 存储系统配置项"}

    key = Column(String(100), unique=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=True, comment="配置值")
    description = Column(String(255), nullable=True, comment="配置描述")
