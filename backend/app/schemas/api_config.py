from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ApiConfigBase(BaseModel):
    """接口配置基础"""
    config_type: str = Field(..., description="配置类型：llm/vin/database/qianxun")
    name: str = Field(..., description="配置名称")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    api_base: Optional[str] = Field(default=None, description="API基础地址")
    api_secret: Optional[str] = Field(default=None, description="API密钥/密码")
    
    # LLM特有
    model: Optional[str] = Field(default=None, description="模型名称")
    temperature: Optional[str] = Field(default="0.1", description="温度参数")
    max_tokens: Optional[int] = Field(default=2000, description="最大Token数")
    prompt_template: Optional[str] = Field(default=None, description="提示词模板")
    
    # 数据库特有
    db_host: Optional[str] = Field(default=None, description="数据库主机")
    db_port: Optional[int] = Field(default=None, description="数据库端口")
    db_name: Optional[str] = Field(default=None, description="数据库名称")
    db_user: Optional[str] = Field(default=None, description="数据库用户名")
    db_password: Optional[str] = Field(default=None, description="数据库密码")
    
    # 千寻微信特有
    wx_id: Optional[str] = Field(default=None, description="微信ID")
    api_url: Optional[str] = Field(default=None, description="API地址")
    
    is_active: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否为默认配置")
    description: Optional[str] = Field(default=None, description="描述")
    sort_order: int = Field(default=0, description="排序")


class ApiConfigCreate(ApiConfigBase):
    """创建接口配置"""
    pass


class ApiConfigUpdate(BaseModel):
    """更新接口配置"""
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_secret: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[str] = None
    max_tokens: Optional[int] = None
    prompt_template: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    wx_id: Optional[str] = None
    api_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class ApiConfig(ApiConfigBase):
    """接口配置响应"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApiConfigList(BaseModel):
    """接口配置列表"""
    list: List[ApiConfig]
    total: int


class VINRecognitionResult(BaseModel):
    """VIN识别结果"""
    vin: str = Field(default="", description="识别出的VIN码")
    greeting: str = Field(default="None", description="节日祝福语，非节假日为None")
    error: Optional[str] = Field(default=None, description="错误信息")
