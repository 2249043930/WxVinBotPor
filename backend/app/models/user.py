"""
用户模型模块
定义用户表结构
"""

from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """用户表 - 存储系统用户信息"""
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    # 基本信息
    nickname = Column(String(50), nullable=False, comment="用户昵称")
    username = Column(String(50), unique=True, nullable=False, comment="登录账号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    phone = Column(String(20), nullable=True, comment="手机号码")
    email = Column(String(100), nullable=True, comment="邮箱地址")
    remark = Column(Text, nullable=True, comment="备注信息")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用：0-禁用，1-启用")
    is_superuser = Column(Boolean, default=False, nullable=False, comment="是否超级管理员：0-否，1-是")

    # 微信关联
    wx_id = Column(String(100), nullable=True, comment="微信ID")
    wx_group_name = Column(String(200), nullable=True, comment="微信群聊名称及wxid")
    group_member_wxid = Column(String(100), nullable=True, comment="群成员wxid")

    # 关联
    logs = relationship("Log", back_populates="user")
    account = relationship("Account", uselist=False, back_populates="user")
