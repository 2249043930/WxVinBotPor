"""
基础模型模块
定义所有模型的基类
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy声明式基类"""
    pass


class BaseModel(Base):
    """基础模型类 - 所有模型的基类"""
    __abstract__ = True

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 软删除标记
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否删除：0-未删除，1-已删除")
