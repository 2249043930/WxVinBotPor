from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from app.models.log import Log, OperationLog


class CRUDLog(CRUDBase[Log]):
    """登录日志CRUD"""

    async def get_logs(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """获取日志列表"""
        query = select(Log).where(Log.is_deleted == False)

        if start_date:
            query = query.where(Log.login_time >= start_date)
        if end_date:
            query = query.where(Log.login_time <= end_date)
        if user_id:
            query = query.where(Log.user_id == user_id)
        if ip_address:
            query = query.where(Log.ip_address.contains(ip_address))

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(Log.login_time.desc())
        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total


class CRUDOperationLog(CRUDBase[OperationLog]):
    """操作日志CRUD"""

    async def get_logs(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        operation_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """获取操作日志列表"""
        query = select(OperationLog).where(OperationLog.is_deleted == False)

        if start_date:
            query = query.where(OperationLog.login_time >= start_date)
        if end_date:
            query = query.where(OperationLog.login_time <= end_date)
        if operation_type:
            query = query.where(OperationLog.operation_type == operation_type)

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(OperationLog.login_time.desc())
        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total


log_crud = CRUDLog(Log)
operation_log_crud = CRUDOperationLog(OperationLog)
