"""
群聊配置CRUD操作
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.group_config import GroupConfig, GroupModelSupplier


class CRUDGroupConfig(CRUDBase[GroupConfig]):
    """群聊配置CRUD"""

    async def get_by_group_id(self, db: AsyncSession, group_id: str, load_relations: bool = True) -> Optional[GroupConfig]:
        """通过群ID获取配置"""
        query = select(GroupConfig).where(GroupConfig.group_id == group_id)
        if load_relations:
            query = query.options(
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model),
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier)
            )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[GroupConfig]:
        """获取多个群聊配置"""
        result = await db.execute(
            select(GroupConfig)
            .options(selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model))
            .options(selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier))
            .offset(skip)
            .limit(limit)
            .order_by(GroupConfig.id.desc())
        )
        return result.scalars().all()

    async def create_with_models(
        self,
        db: AsyncSession,
        *,
        group_id: str,
        group_name: Optional[str] = None,
        customer_service_wxid: Optional[str] = None,
        customer_service_name: Optional[str] = None,
        model_suppliers: List[dict] = None
    ) -> GroupConfig:
        """创建群聊配置（包含车型供应商绑定）"""
        # 创建群聊配置
        config = GroupConfig(
            group_id=group_id,
            group_name=group_name,
            customer_service_wxid=customer_service_wxid,
            customer_service_name=customer_service_name
        )
        db.add(config)
        await db.flush()  # 获取config.id

        # 创建车型供应商绑定
        if model_suppliers:
            for ms in model_suppliers:
                model_supplier = GroupModelSupplier(
                    group_config_id=config.id,
                    car_model_id=ms["car_model_id"],
                    supplier_id=ms["supplier_id"]
                )
                db.add(model_supplier)

        await db.commit()

        # 重新查询配置并预加载关系数据，避免懒加载问题
        result = await db.execute(
            select(GroupConfig)
            .where(GroupConfig.id == config.id)
            .options(
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model),
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier)
            )
        )
        return result.scalar_one()

    async def update_with_models(
        self,
        db: AsyncSession,
        *,
        config_id: int,
        group_name: Optional[str] = None,
        customer_service_wxid: Optional[str] = None,
        customer_service_name: Optional[str] = None,
        model_suppliers: List[dict] = None
    ) -> Optional[GroupConfig]:
        """更新群聊配置（包含车型供应商绑定）"""
        # 获取现有配置（不预加载关系，避免会话问题）
        result = await db.execute(
            select(GroupConfig).where(GroupConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        if not config:
            return None

        # 更新基本信息
        if group_name is not None:
            config.group_name = group_name
        if customer_service_wxid is not None:
            config.customer_service_wxid = customer_service_wxid
        if customer_service_name is not None:
            config.customer_service_name = customer_service_name

        # 更新车型供应商绑定
        if model_suppliers is not None:
            # 先提交基本信息更新，避免关系操作冲突
            await db.flush()

            # 删除旧的绑定
            await db.execute(
                delete(GroupModelSupplier).where(
                    GroupModelSupplier.group_config_id == config_id
                )
            )
            await db.flush()  # 确保删除操作生效

            # 创建新的绑定
            for ms in model_suppliers:
                model_supplier = GroupModelSupplier(
                    group_config_id=config_id,
                    car_model_id=ms["car_model_id"],
                    supplier_id=ms["supplier_id"]
                )
                db.add(model_supplier)

        await db.commit()

        # 重新查询配置并预加载关系数据，避免懒加载问题
        result = await db.execute(
            select(GroupConfig)
            .where(GroupConfig.id == config_id)
            .options(
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model),
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier)
            )
        )
        return result.scalar_one_or_none()

    async def get_supplier_by_model(
        self,
        db: AsyncSession,
        group_id: str,
        car_model_id: int
    ) -> Optional[GroupModelSupplier]:
        """获取群中某个车型的供应商"""
        result = await db.execute(
            select(GroupModelSupplier)
            .join(GroupConfig)
            .options(selectinload(GroupModelSupplier.supplier))
            .where(
                GroupConfig.group_id == group_id,
                GroupModelSupplier.car_model_id == car_model_id
            )
        )
        return result.scalar_one_or_none()


# 创建实例
group_config_crud = CRUDGroupConfig(GroupConfig)
