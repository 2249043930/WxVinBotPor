from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.car_model import MemberType, Supplier, CarModel


class CRUDMemberType(CRUDBase[MemberType]):
    """成员类型CRUD"""
    pass


class CRUDSupplier(CRUDBase[Supplier]):
    """汽配商CRUD"""

    async def get_by_wxid(self, db: AsyncSession, wxid: str) -> Optional[Supplier]:
        """根据wxid获取汽配商"""
        result = await db.execute(
            select(Supplier).where(
                Supplier.wxid == wxid,
                Supplier.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_by_member_type(
        self,
        db: AsyncSession,
        member_type_id: int,
        skip: int = 0,
        limit: int = 20
    ):
        """根据成员类型获取汽配商"""
        query = select(Supplier).where(
            Supplier.member_type_id == member_type_id,
            Supplier.is_deleted == False
        )

        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        suppliers = result.scalars().all()

        return suppliers, total


class CRUDCarModel(CRUDBase[CarModel]):
    """车型CRUD"""

    async def get_by_supplier(
        self,
        db: AsyncSession,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        """根据汽配商获取车型"""
        from app.models.car_model import car_model_supplier

        query = select(CarModel).join(
            car_model_supplier,
            CarModel.id == car_model_supplier.c.car_model_id
        ).where(
            car_model_supplier.c.supplier_id == supplier_id,
            CarModel.is_deleted == False
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def search_by_name(
        self,
        db: AsyncSession,
        name: str,
        skip: int = 0,
        limit: int = 20
    ):
        """根据名称搜索车型"""
        query = select(CarModel).where(
            CarModel.name.contains(name),
            CarModel.is_deleted == False
        )

        count_result = await db.execute(query)
        total = len(count_result.scalars().all())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        models = result.scalars().all()

        return models, total

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[CarModel]:
        """根据名称获取车型（支持模糊匹配）"""
        # 1. 先精确匹配
        result = await db.execute(
            select(CarModel).where(
                CarModel.name == name,
                CarModel.is_deleted == False
            )
        )
        car_model = result.scalar_one_or_none()
        if car_model:
            return car_model
        
        # 2. 模糊匹配
        result = await db.execute(
            select(CarModel).where(
                CarModel.name.contains(name),
                CarModel.is_deleted == False
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_model_info(
        self,
        db: AsyncSession,
        model_info: str
    ) -> Optional[CarModel]:
        """
        根据车型信息（如"奔驰GLC 2017款 GLC 200"）查找车型
        
        匹配逻辑：
        1. 先精确匹配车型名称
        2. 如果没有，尝试从model_info中提取关键信息进行模糊匹配
        """
        # 1. 先精确匹配
        result = await db.execute(
            select(CarModel).where(
                CarModel.name == model_info,
                CarModel.is_deleted == False
            )
        )
        car_model = result.scalar_one_or_none()
        if car_model:
            return car_model
        
        # 2. 模糊匹配 - 尝试匹配model_info中的任何部分
        result = await db.execute(
            select(CarModel).where(
                CarModel.name.contains(model_info),
                CarModel.is_deleted == False
            ).limit(1)
        )
        car_model = result.scalar_one_or_none()
        if car_model:
            return car_model
        
        # 3. 反向匹配 - 尝试找到包含车型名称的记录
        # 提取model_info中的关键词（如品牌、车型）
        import re
        # 提取中文和英文/数字组合
        keywords = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z0-9]+', model_info)
        
        for keyword in keywords:
            if len(keyword) >= 2:  # 至少2个字符
                result = await db.execute(
                    select(CarModel).where(
                        CarModel.name.contains(keyword),
                        CarModel.is_deleted == False
                    ).limit(1)
                )
                car_model = result.scalar_one_or_none()
                if car_model:
                    return car_model
        
        return None

    async def get_suppliers_by_model(
        self,
        db: AsyncSession,
        model_name: str
    ) -> List[dict]:
        """
        根据车型名称获取相关供应商

        匹配逻辑：
        1. 先精确匹配车型名称
        2. 如果没有，模糊匹配车型名称
        3. 获取该车型的所有供应商
        """
        from app.models.car_model import car_model_supplier

        try:
            # 1. 精确匹配车型
            query = select(CarModel).where(
                CarModel.name == model_name,
                CarModel.is_deleted == False
            )
            result = await db.execute(query)
            car_model = result.scalar_one_or_none()

            # 2. 如果没有精确匹配，尝试模糊匹配
            if not car_model:
                query = select(CarModel).where(
                    CarModel.name.contains(model_name),
                    CarModel.is_deleted == False
                ).limit(1)
                result = await db.execute(query)
                car_model = result.scalar_one_or_none()

            if not car_model:
                return []

            # 3. 获取该车型的所有供应商
            query = select(Supplier).join(
                car_model_supplier,
                Supplier.id == car_model_supplier.c.supplier_id
            ).where(
                car_model_supplier.c.car_model_id == car_model.id,
                Supplier.is_deleted == False
            )

            result = await db.execute(query)
            suppliers = result.scalars().all()

            # 转换为字典列表
            return [
                {
                    "id": s.id,
                    "wxid": s.wxid,
                    "nick": s.nick,
                    "name": s.name,
                    "phone": s.phone
                }
                for s in suppliers
            ]

        except Exception as e:
            from loguru import logger
            logger.error(f"获取供应商失败: {e}")
            return []


member_type_crud = CRUDMemberType(MemberType)
supplier_crud = CRUDSupplier(Supplier)
car_model_crud = CRUDCarModel(CarModel)
