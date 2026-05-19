"""
message模型模块
定义message表结构
"""

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from app.models.base import BaseModel


class MessageRecord(BaseModel):
    """消息记录表 - 接收的微信消息"""
    __tablename__ = "message_records"
    __table_args__ = {"comment": "消息记录表 - 存储群聊消息"}

    # 消息信息
    msg_type = Column(String(50), nullable=False, comment="消息类型：text/image/voice")
    image_content = Column(LONGTEXT, nullable=True, comment="图片内容（URL或Base64）")
    msg_date = Column(DateTime, nullable=False, comment="日期")

    # 人员信息
    inquirer = Column(String(100), nullable=True, comment="询价人")
    vin_code = Column(String(50), nullable=True, comment="车架号")
    car_model = Column(String(200), nullable=True, comment="车型")
    source_group = Column(String(200), nullable=True, comment="来源群")

    # 原始消息
    raw_message = Column(Text, nullable=True, comment="原始消息内容")
