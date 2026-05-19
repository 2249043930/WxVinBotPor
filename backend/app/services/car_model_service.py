from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.car_model import member_type_crud, supplier_crud, car_model_crud
from app.schemas.car_model import MemberType, Supplier, CarModel


class CarModelService:
    """车型配置服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_member_types(self) -> List[MemberType]:
        """获取成员类型列表"""
        types = await member_type_crud.get_multi(self.db)
        return types

    async def create_member_type(self, name: str, description: str = None) -> MemberType:
        """创建成员类型"""
        type_data = {"name": name, "description": description}
        return await member_type_crud.create(self.db, obj_in=type_data)

    async def get_suppliers(self, page: int = 1, page_size: int = 20):
        """获取汽配商列表"""
        skip = (page - 1) * page_size
        suppliers, total = await supplier_crud.get_multi(
            self.db, skip=skip, limit=page_size
        )
        return {
            "list": suppliers,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def create_supplier(self, wxid: str, name: str, member_type_id: int = None) -> Supplier:
        """创建汽配商"""
        # 检查wxid是否已存在
        existing = await supplier_crud.get_by_wxid(self.db, wxid)
        if existing:
            raise ValueError("汽配商wxid已存在")

        supplier_data = {
            "wxid": wxid,
            "name": name,
            "member_type_id": member_type_id
        }
        return await supplier_crud.create(self.db, obj_in=supplier_data)

    async def get_car_models(self, supplier_wxid: Optional[str] = None) -> List[dict]:
        """获取车型列表 - 返回树形结构"""
        if supplier_wxid:
            supplier = await supplier_crud.get_by_wxid(self.db, supplier_wxid)
            if supplier:
                models = await car_model_crud.get_by_supplier(self.db, supplier.id)
            else:
                return []
        else:
            models = await car_model_crud.get_multi(self.db, limit=1000)
        
        # 按品牌分组，构建树形结构
        brand_dict = {}
        for model in models:
            brand = model.brand or "其他"
            if brand not in brand_dict:
                brand_dict[brand] = {
                    "id": f"brand_{brand}",
                    "name": brand,
                    "children": []
                }
            brand_dict[brand]["children"].append({
                "id": model.id,
                "name": model.name,
                "brand": model.brand,
                "series": model.series
            })
        
        return list(brand_dict.values())

    async def create_car_model(
        self,
        name: str,
        brand: str = None,
        series: str = None,
        displacement: str = None,
        year: str = None
    ) -> CarModel:
        """创建车型"""
        model_data = {
            "name": name,
            "brand": brand,
            "series": series,
            "displacement": displacement,
            "year": year
        }
        return await car_model_crud.create(self.db, obj_in=model_data)

    async def assign_car_models_to_supplier(self, supplier_id: int, car_model_ids: List[int]):
        """为汽配商分配车型"""
        from app.models.car_model import car_model_supplier

        # 先删除现有关系
        await self.db.execute(
            car_model_supplier.delete().where(
                car_model_supplier.c.supplier_id == supplier_id
            )
        )

        # 添加新关系
        for car_model_id in car_model_ids:
            await self.db.execute(
                car_model_supplier.insert().values(
                    supplier_id=supplier_id,
                    car_model_id=car_model_id
                )
            )

        await self.db.flush()
