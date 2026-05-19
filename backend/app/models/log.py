"""
log模型模块
定义log表结构
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Log(BaseModel):
    """日志表 - 记录用户登录和操作"""
    __tablename__ = "logs"
    __table_args__ = {"comment": "日志表 - 存储操作日志"}

    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id", comment="主键ID"), nullable=True, comment="用户ID")
    nickname = Column(String(50), nullable=True, comment="用户昵称")

    # 设备信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    login_location = Column(String(200), nullable=True, comment="登录地点")
    os = Column(String(100), nullable=True, comment="操作系统")
    browser = Column(String(100), nullable=True, comment="浏览器")

    # 时间
    login_time = Column(DateTime, nullable=False, comment="登录时间")

    # 关联
    user = relationship("User", back_populates="logs")


class OperationLog(BaseModel):
    """日志记录表 - 系统操作日志"""
    __tablename__ = "operation_logs"

    # 用户信息
    nickname = Column(String(50), nullable=True, comment="用户昵称")

    # 设备信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    login_location = Column(String(200), nullable=True, comment="登录地点")
    os = Column(String(100), nullable=True, comment="操作系统")
    browser = Column(String(100), nullable=True, comment="浏览器")
    login_time = Column(DateTime, nullable=False, comment="登录时间")

    # 操作信息
    operation = Column(String(200), nullable=True, comment="操作内容")
    operation_type = Column(String(50), nullable=True, comment="操作类型")
