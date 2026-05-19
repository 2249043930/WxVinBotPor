from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.message import MessageRecord


class CRUDMessage(CRUDBase[MessageRecord]):
    """消息记录CRUD"""

    async def get_records(
        self,
        db: AsyncSession,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        msg_type: Optional[str] = None,
        source_group: Optional[str] = None,
        inquirer: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """获取消息记录列表"""
        query = select(MessageRecord).where(MessageRecord.is_deleted == False)

        if start_date:
            query = query.where(MessageRecord.msg_date >= start_date)
        if end_date:
            query = query.where(MessageRecord.msg_date <= end_date)
        if msg_type:
            query = query.where(MessageRecord.msg_type == msg_type)
        if source_group:
            query = query.where(MessageRecord.source_group.contains(source_group))
        if inquirer:
            query = query.where(MessageRecord.inquirer.contains(inquirer))

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(MessageRecord.msg_date.desc())
        result = await db.execute(query)
        records = result.scalars().all()

        return records, total


message_crud = CRUDMessage(MessageRecord)
