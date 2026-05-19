"""接口配置API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.api_config import (
    ApiConfig, ApiConfigCreate, ApiConfigUpdate, 
    ApiConfigList, VINRecognitionResult
)
from app.services.api_config_service import ApiConfigService, VINRecognizer
from pydantic import BaseModel

router = APIRouter()


class VINRecognitionRequest(BaseModel):
    """VIN识别请求"""
    image: str  # Base64编码的图片
    config_id: Optional[int] = None  # 指定配置ID，不传则使用默认配置


@router.get("/list")
async def get_config_list(
    config_type: Optional[str] = Query(None, description="配置类型：llm/vin/database/qianxun"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取接口配置列表"""
    service = ApiConfigService(db)
    result = await service.get_list(config_type=config_type, page=page, page_size=page_size)
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.get("/{config_id}")
async def get_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个配置"""
    service = ApiConfigService(db)
    config = await service.get_by_id(config_id)
    if not config:
        return {
            "code": 1,
            "message": "配置不存在",
            "data": None
        }
    return {
        "code": 0,
        "message": "success",
        "data": config
    }


@router.post("/create")
async def create_config(
    config: ApiConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建配置"""
    service = ApiConfigService(db)
    result = await service.create(config)
    return {
        "code": 0,
        "message": "创建成功",
        "data": result
    }


@router.put("/update/{config_id}")
async def update_config(
    config_id: int,
    config: ApiConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新配置"""
    service = ApiConfigService(db)
    result = await service.update(config_id, config)
    if not result:
        return {
            "code": 1,
            "message": "配置不存在",
            "data": None
        }
    return {
        "code": 0,
        "message": "更新成功",
        "data": result
    }


@router.delete("/delete/{config_id}")
async def delete_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除配置"""
    service = ApiConfigService(db)
    success = await service.delete(config_id)
    if not success:
        return {
            "code": 1,
            "message": "配置不存在",
            "data": None
        }
    return {
        "code": 0,
        "message": "删除成功",
        "data": None
    }


@router.post("/recognize")
async def recognize_vin(
    request: VINRecognitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """识别图片中的VIN码
    
    请求体: {"image": "base64编码的图片", "config_id": 配置ID（可选）}
    返回: {"vin": "识别的VIN码", "greeting": "祝福语或None"}
    """
    service = ApiConfigService(db)
    
    # 获取配置
    if request.config_id:
        config = await service.get_by_id(request.config_id)
    else:
        config = await service.get_default_by_type("llm")
    
    if not config:
        return {
            "code": 1,
            "message": "未找到可用的LLM配置",
            "data": None
        }
    
    if not config.is_active:
        return {
            "code": 1,
            "message": "该配置已禁用",
            "data": None
        }
    
    recognizer = VINRecognizer(config)
    result = await recognizer.recognize_vin(request.image)
    
    return {
        "code": 0,
        "message": "success",
        "data": result
    }
