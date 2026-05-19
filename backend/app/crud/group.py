from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.group import WechatGroup


class CRUDGroup(CRUDBase[WechatGroup]):
    """微信群CRUD"""

    async def get_by_group_id(self, db: AsyncSession, group_id: str) -> Optional[WechatGroup]:
        """根据群ID获取群"""
        result = await db.execute(
            select(WechatGroup).where(
                WechatGroup.group_id == group_id,
                WechatGroup.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def search_groups(
        self,
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """搜索群"""
        query = select(WechatGroup).where(WechatGroup.is_deleted == False)

        if keyword:
            query = query.where(WechatGroup.group_name.contains(keyword))
        if is_active is not None:
            query = query.where(WechatGroup.is_active == is_active)

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(WechatGroup.created_at.desc())
        result = await db.execute(query)
        groups = result.scalars().all()

        return groups, total

    async def get_active_groups(self, db: AsyncSession) -> List[WechatGroup]:
        """获取所有启用的群"""
        result = await db.execute(
            select(WechatGroup).where(
                WechatGroup.is_active == True,
                WechatGroup.is_deleted == False
            )
        )
        return result.scalars().all()


group_crud = CRUDGroup(WechatGroup)
