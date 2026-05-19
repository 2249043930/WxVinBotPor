from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.message import message_crud


class StatisticsService:
    """统计服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_message_records(
        self,
        page: int = 1,
        page_size: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        msg_type: Optional[str] = None,
        source_group: Optional[str] = None,
        inquirer: Optional[str] = None
    ):
        """获取消息记录"""
        skip = (page - 1) * page_size
        records, total = await message_crud.get_records(
            self.db,
            start_date=start_date,
            end_date=end_date,
            msg_type=msg_type,
            source_group=source_group,
            inquirer=inquirer,
            skip=skip,
            limit=page_size
        )

        return {
            "list": records,
            "total": total,
            "page": page,
            "page_size": page_size
        }
