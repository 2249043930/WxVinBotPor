"""
群成员模型
存储每个群聊的成员信息，用于智能同步功能
"""

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class GroupMember(BaseModel):
    """群成员表 - 存储群聊成员信息"""
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint('group_id', 'wxid', name='uix_group_member'),
        {"comment": "群成员表 - 存储群聊成员信息"}
    )

    # 外键 - 关联到群聊
    group_id = Column(String(200), ForeignKey("wechat_groups.group_id"), nullable=False, index=True, comment="群ID")
    
    # 成员信息
    wxid = Column(String(100), nullable=False, index=True, comment="成员wxid")
    nick = Column(String(100), nullable=True, comment="昵称")
    group_nick = Column(String(100), nullable=True, comment="群昵称")
    
    # 关联
    group = relationship("WechatGroup", foreign_keys=[group_id], primaryjoin="GroupMember.group_id == WechatGroup.group_id")

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "wxid": self.wxid,
            "nick": self.nick,
            "group_nick": self.group_nick,
            "display_name": f"{self.group_nick or self.nick} ({self.wxid})" if (self.group_nick or self.nick) else self.wxid,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }
