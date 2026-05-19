from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/message")
async def get_message_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    msg_type: Optional[str] = None,
    source_group: Optional[str] = None,
    inquirer: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取消息统计记录"""
    service = StatisticsService(db)
    result = await service.get_message_records(
        page, page_size, start_date, end_date,
        msg_type, source_group, inquirer
    )
    return {
        "code": 0,
        "message": "success",
        "data": result
    }
