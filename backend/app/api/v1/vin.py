from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.vin import VinRecordList, VinRecordDetail
from app.services.vin_service import VinRecordService

router = APIRouter()


@router.get("/record")
async def get_vin_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    recognize_status: Optional[str] = None,
    vin_code: Optional[str] = None,
    car_model: Optional[str] = None,
    source_group: Optional[str] = None,
    is_quoted: Optional[bool] = None,
    supplier: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求数据统计 - 获取车架号记录列表"""
    service = VinRecordService(db)
    result = await service.get_records(
        page, page_size, start_date, end_date,
        recognize_status, vin_code, car_model,
        source_group, is_quoted, supplier
    )
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.get("/record/{record_id}")
async def get_vin_record_detail(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取车架号记录详情"""
    service = VinRecordService(db)
    result = await service.get_detail(record_id)
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.delete("/record/{record_id}")
async def delete_vin_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除车架号记录"""
    service = VinRecordService(db)
    await service.delete(record_id)
    return {
        "code": 0,
        "message": "删除成功",
        "data": None
    }
