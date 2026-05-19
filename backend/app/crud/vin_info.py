"""
VIN信息CRUD操作
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.crud.base import CRUDBase
from app.models.vin_info import VinInfo


class CRUDVinInfo(CRUDBase[VinInfo]):
    """VIN信息CRUD"""

    async def get_by_vin(self, db: AsyncSession, vin_code: str) -> Optional[VinInfo]:
        """根据VIN码查询"""
        result = await db.execute(
            select(self.model).where(
                self.model.vin_code == vin_code,
                self.model.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def create_or_update(self, db: AsyncSession, vin_data: Dict[str, Any]) -> VinInfo:
        """创建或更新VIN信息"""
        vin_code = vin_data.get("vin") or vin_data.get("vin_code")
        
        # 查询是否已存在
        existing = await self.get_by_vin(db, vin_code)
        
        if existing:
            # 更新现有记录
            update_data = {
                "manufacturer": vin_data.get("manufacturer"),
                "brand": vin_data.get("brand"),
                "car_model": vin_data.get("model_info") or vin_data.get("car_model"),
                "series": vin_data.get("series"),
                "displacement": vin_data.get("displacement"),
                "year": vin_data.get("year"),
                "typename": vin_data.get("typename"),
                "enginemodel": vin_data.get("enginemodel"),
                "sizetype": vin_data.get("sizetype"),
                "geartype": vin_data.get("geartype"),
                "fronttiresize": vin_data.get("fronttiresize"),
                "reartiresize": vin_data.get("reartiresize"),
                "volume": vin_data.get("volume"),
                "viscosity": vin_data.get("viscosity"),
                "grade": vin_data.get("grade"),
                "level": vin_data.get("level"),
                "source": vin_data.get("source", "jisu_api"),
            }
            
            # 更新记录
            for key, value in update_data.items():
                if value is not None:
                    setattr(existing, key, value)
            
            # 增加查询次数
            existing.query_count += 1
            
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # 创建新记录
            create_data = {
                "vin_code": vin_code,
                "manufacturer": vin_data.get("manufacturer"),
                "brand": vin_data.get("brand"),
                "car_model": vin_data.get("model_info") or vin_data.get("car_model"),
                "series": vin_data.get("series"),
                "displacement": vin_data.get("displacement"),
                "year": vin_data.get("year"),
                "typename": vin_data.get("typename"),
                "enginemodel": vin_data.get("enginemodel"),
                "sizetype": vin_data.get("sizetype"),
                "geartype": vin_data.get("geartype"),
                "fronttiresize": vin_data.get("fronttiresize"),
                "reartiresize": vin_data.get("reartiresize"),
                "volume": vin_data.get("volume"),
                "viscosity": vin_data.get("viscosity"),
                "grade": vin_data.get("grade"),
                "level": vin_data.get("level"),
                "source": vin_data.get("source", "jisu_api"),
                "query_count": 1
            }
            
            db_obj = self.model(**create_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj


# 导出实例
vin_info_crud = CRUDVinInfo(VinInfo)
