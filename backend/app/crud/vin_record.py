"""
VIN记录CRUD操作
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.vin_record import VinRecord


class CRUDVinRecord(CRUDBase[VinRecord]):
    """VIN记录CRUD"""

    async def get_by_vin(self, db: AsyncSession, vin_code: str) -> Optional[VinRecord]:
        """根据VIN码查询"""
        result = await db.execute(
            select(self.model).where(
                self.model.vin_code == vin_code,
                self.model.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_records(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """获取VIN记录列表"""
        query = select(VinRecord).where(VinRecord.is_deleted == False)

        if start_date:
            query = query.where(VinRecord.inquiry_time >= start_date)
        if end_date:
            query = query.where(VinRecord.inquiry_time <= end_date)
        if status:
            query = query.where(VinRecord.status == status)
        if group_id:
            query = query.where(VinRecord.group_id == group_id)

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(VinRecord.inquiry_time.desc())
        result = await db.execute(query)
        records = result.scalars().all()

        return records, total


# 导出实例
vin_record = CRUDVinRecord(VinRecord)
