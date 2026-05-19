from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.crud.base import CRUDBase
from app.models.statistics import Statistics


class CRUDStatistics(CRUDBase[Statistics]):
    """统计CRUD"""

    async def get_records(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        recognize_status: Optional[str] = None,
        vin_code: Optional[str] = None,
        car_model: Optional[str] = None,
        source_group: Optional[str] = None,
        is_quoted: Optional[bool] = None,
        supplier: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """获取统计记录列表"""
        query = select(Statistics).where(Statistics.is_deleted == False)

        if start_date:
            query = query.where(Statistics.date >= start_date)
        if end_date:
            query = query.where(Statistics.date <= end_date)
        if recognize_status:
            query = query.where(Statistics.recognize_status == recognize_status)
        if vin_code:
            query = query.where(Statistics.vin_code.contains(vin_code))
        if car_model:
            query = query.where(Statistics.car_model.contains(car_model))
        if source_group:
            query = query.where(Statistics.source_group.contains(source_group))
        if is_quoted is not None:
            query = query.where(Statistics.is_quoted == is_quoted)
        if supplier:
            query = query.where(Statistics.supplier.contains(supplier))

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(Statistics.date.desc())
        result = await db.execute(query)
        records = result.scalars().all()

        return records, total

    async def get_stats_by_date_range(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """获取日期范围内的统计"""
        # 总数
        total_result = await db.execute(
            select(func.count(Statistics.id)).where(
                and_(
                    Statistics.date >= start_date,
                    Statistics.date <= end_date,
                    Statistics.is_deleted == False
                )
            )
        )
        total = total_result.scalar() or 0

        # 成功数
        success_result = await db.execute(
            select(func.count(Statistics.id)).where(
                and_(
                    Statistics.date >= start_date,
                    Statistics.date <= end_date,
                    Statistics.recognize_status == "success",
                    Statistics.is_deleted == False
                )
            )
        )
        success = success_result.scalar() or 0

        return {
            "total": total,
            "success": success,
            "fail": total - success
        }

    async def create_inquiry_record(
        self,
        db: AsyncSession,
        vin: str,
        model_info: str,
        inquirer_name: str,
        group_id: str,
        quoter_name: Optional[str] = None,
        recognize_status: str = "success"
    ) -> Statistics:
        """
        创建询价记录

        Args:
            vin: VIN码
            model_info: 车型信息
            inquirer_name: 询价人昵称
            group_id: 群ID
            quoter_name: 报价人（供应商）名称
            recognize_status: 识别状态

        Returns:
            创建的统计记录
        """
        record = Statistics(
            vin_code=vin,
            car_model=model_info,
            source_group=group_id,
            inquirer=inquirer_name,
            quoter=quoter_name,
            recognize_status=recognize_status,
            date=datetime.now(),
            is_quoted=False
        )

        db.add(record)
        await db.commit()
        await db.refresh(record)

        return record


statistics_crud = CRUDStatistics(Statistics)
