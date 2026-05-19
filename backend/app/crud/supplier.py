"""
供应商CRUD操作
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.car_model import Supplier


class CRUDSupplier(CRUDBase[Supplier]):
    """供应商CRUD"""

    async def get_by_wxid(self, db: AsyncSession, wxid: str) -> Optional[Supplier]:
        """通过wxid获取供应商"""
        result = await db.execute(
            select(Supplier).where(Supplier.wxid == wxid, Supplier.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Supplier]:
        """获取多个供应商"""
        result = await db.execute(
            select(Supplier)
            .where(Supplier.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(Supplier.id.desc())
        )
        return result.scalars().all()

    async def create_supplier(
        self,
        db: AsyncSession,
        *,
        wxid: str,
        name: str,
        phone: Optional[str] = None,
        member_type_id: Optional[int] = None
    ) -> Supplier:
        """创建供应商"""
        supplier = Supplier(
            wxid=wxid,
            name=name,
            phone=phone,
            member_type_id=member_type_id
        )
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)
        return supplier


# 创建实例
supplier_crud = CRUDSupplier(Supplier)
