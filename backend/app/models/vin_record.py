"""
VIN记录模型
存储VIN识别的原始记录
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from app.models.base import BaseModel
from datetime import datetime


class VinRecord(BaseModel):
    """VIN记录表 - 存储VIN识别的原始记录"""
    __tablename__ = "vin_records"
    __table_args__ = {"comment": "VIN记录表 - 存储VIN识别的原始记录"}

    # VIN信息
    vin_code = Column(String(50), nullable=True, comment="车架号")
    car_model = Column(String(200), nullable=True, comment="车型")

    # 群聊信息
    group_id = Column(String(100), nullable=True, comment="群ID")
    group_name = Column(String(200), nullable=True, comment="群名称")

    # 发送者信息
    sender_wxid = Column(String(100), nullable=True, comment="发送者wxid")
    sender_nick = Column(String(100), nullable=True, comment="发送者昵称")

    # 消息内容
    msg_content = Column(Text, nullable=True, comment="消息内容")
    image_content = Column(LONGTEXT, nullable=True, comment="图片内容（Base64）")

    # 识别状态
    status = Column(String(20), nullable=True, default="pending", comment="状态：success/fail/pending")
    error_msg = Column(Text, nullable=True, comment="错误信息")

    # 时间
    inquiry_time = Column(DateTime, default=datetime.now, comment="查询时间")
