from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.log import LogList
from app.services.log_service import LogService

router = APIRouter()


@router.get("/login")
async def get_login_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求系统管理 - 登录日志

    包含字段：
    - IP地址
    - 登录地点归属查询
    - 操作系统
    - 浏览器
    - 登录时间
    """
    service = LogService(db)
    result = await service.get_login_logs(
        page, page_size, start_date, end_date, user_id, ip_address
    )
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.get("/operation")
async def get_operation_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    operation_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取操作日志"""
    service = LogService(db)
    result = await service.get_operation_logs(
        page, page_size, start_date, end_date, operation_type
    )
    return {
        "code": 0,
        "message": "success",
        "data": result
    }
