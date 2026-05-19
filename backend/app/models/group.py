"""
group模型模块
定义group表结构
"""

from sqlalchemy import Column, String, Integer, Boolean, Time, Text
from app.models.base import BaseModel


class WechatGroup(BaseModel):
    """微信群表"""
    __tablename__ = "wechat_groups"
    __table_args__ = {"comment": "微信群表 - 存储群聊信息"}

    # 基本信息
    group_name = Column(String(200), nullable=False, comment="群名称")
    group_id = Column(String(100), unique=True, nullable=False, comment="群ID")
    member_count = Column(Integer, default=0, nullable=False, comment="成员数")

    # 状态
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")

    # 通知配置
    inquiry_notify = Column(Boolean, default=True, nullable=False, comment="询价通知")
    quote_notify = Column(Boolean, default=True, nullable=False, comment="报价通知")
    delivery_notify = Column(Boolean, default=True, nullable=False, comment="发货通知")
    deal_notify = Column(Boolean, default=True, nullable=False, comment="成交通知")

    # 工作时间
    work_start_time = Column(Time, nullable=True, comment="工作开始时间")
    work_end_time = Column(Time, nullable=True, comment="工作结束时间")

    # 关键字触发
    notify_keywords = Column(Text, nullable=True, comment="通知触发关键字")
