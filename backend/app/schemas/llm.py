from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LLMProvider(BaseModel):
    """LLM服务商配置"""
    id: Optional[int] = None
    name: str = Field(..., description="服务商名称，如：kimi、豆包、OpenAI")
    api_key: str = Field(..., description="API密钥")
    api_base: str = Field(..., description="API基础地址")
    model: str = Field(..., description="模型名称，如：moonshot-v1-8k-vision-preview")
    is_active: bool = Field(default=True, description="是否启用")
    is_default: bool = Field(default=False, description="是否为默认模型")
    description: Optional[str] = Field(default=None, description="描述")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LLMProviderCreate(BaseModel):
    """创建LLM服务商"""
    name: str
    api_key: str
    api_base: str
    model: str
    is_active: bool = True
    is_default: bool = False
    description: Optional[str] = None


class LLMProviderUpdate(BaseModel):
    """更新LLM服务商"""
    name: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None


class VINRecognitionResult(BaseModel):
    """VIN识别结果"""
    vin: str = Field(default="", description="识别出的VIN码")
    greeting: str = Field(default="None", description="节日祝福语，非节假日为None")
    error: Optional[str] = Field(default=None, description="错误信息")
