from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase[User]):
    """用户CRUD"""

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).where(
                User.username == username,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(
            select(User).where(
                User.email == email,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, db: AsyncSession, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await db.execute(
            select(User).where(
                User.phone == phone,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_wx_id(self, db: AsyncSession, wx_id: str) -> Optional[User]:
        """根据微信ID获取用户"""
        result = await db.execute(
            select(User).where(
                User.wx_id == wx_id,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def search_users(
        self,
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """搜索用户"""
        query = select(User).where(User.is_deleted == False)

        if keyword:
            query = query.where(
                (User.username.contains(keyword)) |
                (User.nickname.contains(keyword)) |
                (User.phone.contains(keyword))
            )

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # 获取总数
        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        # 分页
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()

        return users, total


user_crud = CRUDUser(User)
