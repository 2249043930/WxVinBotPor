"""接口配置模型"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.models.base import BaseModel


class ApiConfig(BaseModel):
    """接口配置表"""
    __tablename__ = "api_configs"
    __table_args__ = {"comment": "接口配置表 - 存储API接口配置"}

    config_type = Column(String(50), nullable=False, comment="配置类型：llm/vin/database/qianxun")
    name = Column(String(100), nullable=False, comment="配置名称")
    
    # 通用字段
    api_key = Column(String(500), nullable=True, comment="API密钥")
    api_base = Column(String(500), nullable=True, comment="API基础地址")
    api_secret = Column(String(500), nullable=True, comment="API密钥/密码")
    
    # LLM特有字段
    model = Column(String(100), nullable=True, comment="模型名称")
    temperature = Column(String(10), nullable=True, default="0.1", comment="温度参数")
    max_tokens = Column(Integer, nullable=True, default=2000, comment="最大Token数")
    prompt_template = Column(Text, nullable=True, comment="提示词模板")
    
    # 数据库特有字段
    db_host = Column(String(100), nullable=True, comment="数据库主机")
    db_port = Column(Integer, nullable=True, comment="数据库端口")
    db_name = Column(String(100), nullable=True, comment="数据库名称")
    db_user = Column(String(100), nullable=True, comment="数据库用户名")
    db_password = Column(String(200), nullable=True, comment="数据库密码")
    
    # 千寻微信特有字段
    wx_id = Column(String(100), nullable=True, comment="微信ID")
    api_url = Column(String(500), nullable=True, comment="API地址")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否为默认配置")
    description = Column(String(500), nullable=True, comment="描述")
    sort_order = Column(Integer, default=0, comment="排序")
