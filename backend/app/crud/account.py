from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.account import Account


class CRUDAccount(CRUDBase[Account]):
    """账户CRUD"""

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Account]:
        """根据用户ID获取账户"""
        result = await db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def update_stats(self, db: AsyncSession, user_id: int, success: bool):
        """更新统计信息"""
        account = await self.get_by_user_id(db, user_id)
        if not account:
            # 创建新账户
            account = Account(user_id=user_id)
            db.add(account)
            await db.flush()

        if success:
            account.llm_success_count += 1
        else:
            account.llm_fail_count += 1

        # 计算成功率
        total = account.llm_success_count + account.llm_fail_count
        if total > 0:
            account.llm_success_rate = account.llm_success_count / total

        await db.flush()
        await db.refresh(account)
        return account


account_crud = CRUDAccount(Account)
