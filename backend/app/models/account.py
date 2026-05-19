"""
account模型模块
定义account表结构
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Account(BaseModel):
    """账户管理表 - 记录LLM使用情况"""
    __tablename__ = "accounts"
    __table_args__ = {"comment": "账号表 - 存储微信账号信息"}

    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id", comment="主键ID"), unique=True, nullable=False, comment="用户ID")

    # LLM统计
    llm_success_count = Column(Integer, default=0, nullable=False, comment="LLM识别成功次数")
    llm_fail_count = Column(Integer, default=0, nullable=False, comment="LLM识别失败次数")
    llm_success_rate = Column(Float, default=0.0, nullable=False, comment="LLM识别成功率")

    # 关联
    user = relationship("User", back_populates="account")
