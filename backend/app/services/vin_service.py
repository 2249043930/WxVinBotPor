from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.statistics import statistics_crud
from app.schemas.vin import VinRecordList, VinRecordDetail


class VinRecordService:
    """车架号记录服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_records(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        recognize_status: Optional[str] = None,
        vin_code: Optional[str] = None,
        car_model: Optional[str] = None,
        source_group: Optional[str] = None,
        is_quoted: Optional[bool] = None,
        supplier: Optional[str] = None
    ) -> VinRecordList:
        """获取车架号记录列表"""
        skip = (page - 1) * page_size
        records, total = await statistics_crud.get_records(
            self.db,
            start_date=start_date,
            end_date=end_date,
            recognize_status=recognize_status,
            vin_code=vin_code,
            car_model=car_model,
            source_group=source_group,
            is_quoted=is_quoted,
            supplier=supplier,
            skip=skip,
            limit=page_size
        )

        return {
            "list": records,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def get_detail(self, record_id: int) -> dict:
        """获取车架号记录详情"""
        from app.models.statistics import Statistics
        from app.crud.base import CRUDBase

        crud = CRUDBase(Statistics)
        record = await crud.get(self.db, id=record_id)

        if not record:
            raise ValueError("记录不存在")

        return {
            "id": record.id,
            "date": record.date,
            "recognize_status": record.recognize_status,
            "vin_code": record.vin_code,
            "car_model": record.car_model,
            "source_group": record.source_group,
            "inquirer": record.inquirer,
            "quoter": record.quoter,
            "is_quoted": record.is_quoted,
            "quote_time": record.quote_time,
            "supplier": record.supplier,
            "raw_data": None,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }

    async def delete(self, record_id: int):
        """删除车架号记录"""
        from app.models.statistics import Statistics
        from app.crud.base import CRUDBase

        crud = CRUDBase(Statistics)
        record = await crud.get(self.db, id=record_id)
        if not record:
            raise ValueError("记录不存在")

        await crud.delete(self.db, id=record_id)
