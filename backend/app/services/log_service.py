from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.log import log_crud, operation_log_crud
from app.schemas.log import LogList, OperationLogRecord


class LogService:
    """日志服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_login_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> LogList:
        """获取登录日志"""
        skip = (page - 1) * page_size
        logs, total = await log_crud.get_logs(
            self.db,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            ip_address=ip_address,
            skip=skip,
            limit=page_size
        )

        return LogList(
            list=logs,
            total=total,
            page=page,
            page_size=page_size
        )

    async def get_operation_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        operation_type: Optional[str] = None
    ):
        """获取操作日志"""
        skip = (page - 1) * page_size
        logs, total = await operation_log_crud.get_logs(
            self.db,
            start_date=start_date,
            end_date=end_date,
            operation_type=operation_type,
            skip=skip,
            limit=page_size
        )

        return {
            "list": logs,
            "total": total,
            "page": page,
            "page_size": page_size
        }
