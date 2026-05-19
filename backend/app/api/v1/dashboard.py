from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.dashboard import DashboardStats, ChartData
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求首页展示 - 获取看板统计数据"""
    service = DashboardService(db)
    data = await service.get_stats()
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.get("/charts")
async def get_chart_data(
    chart_type: str = "all",
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取图表数据"""
    service = DashboardService(db)
    data = await service.get_chart_data(chart_type, days)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.get("/recent-records")
async def get_recent_records(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取最近识别记录"""
    service = DashboardService(db)
    data = await service.get_recent_records(limit)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.get("/hot-models")
async def get_hot_models(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取热门车型排行"""
    service = DashboardService(db)
    data = await service.get_hot_models(limit)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }
