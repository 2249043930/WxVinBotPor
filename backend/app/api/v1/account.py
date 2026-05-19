from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/llm-stats")
async def get_llm_statistics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取LLM识别统计数据"""
    service = AccountService(db)
    result = await service.get_llm_stats()
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.get("/daily-stats")
async def get_daily_statistics(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取每日识别统计"""
    service = AccountService(db)
    result = await service.get_daily_stats(
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    return {
        "code": 0,
        "message": "success",
        "data": result
    }
