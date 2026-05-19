from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.car_model import (
    MemberType, MemberTypeCreate,
    Supplier, SupplierCreate,
    CarModel, CarModelCreate
)
from app.services.car_model_service import CarModelService

router = APIRouter()


@router.get("/member-type", response_model=List[MemberType])
async def get_member_types(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求车型配置 - 获取成员类型列表

    类型：客户、业务员、客服
    """
    service = CarModelService(db)
    return await service.get_member_types()


@router.post("/member-type", response_model=MemberType)
async def create_member_type(
    data: MemberTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建成员类型"""
    service = CarModelService(db)
    return await service.create_member_type(data.name, data.description)


@router.get("/supplier")
async def get_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取汽配商列表"""
    service = CarModelService(db)
    return await service.get_suppliers(page, page_size)


@router.post("/supplier", response_model=Supplier)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建汽配商"""
    service = CarModelService(db)
    return await service.create_supplier(data.wxid, data.name, data.member_type_id)


@router.get("/car-model")
async def get_car_models(
    supplier_wxid: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取车型列表 - 返回树形结构"""
    service = CarModelService(db)
    data = await service.get_car_models(supplier_wxid)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.post("/car-model")
async def create_car_model(
    data: CarModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建车型"""
    service = CarModelService(db)
    car_model = await service.create_car_model(
        data.name, data.brand, data.series, data.displacement, data.year
    )
    return {
        "code": 0,
        "message": "创建成功",
        "data": car_model
    }


@router.put("/car-model/{car_model_id}")
async def update_car_model(
    car_model_id: int,
    data: CarModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新车型"""
    from app.crud.car_model import car_model_crud
    
    car_model = await car_model_crud.get(db, id=car_model_id)
    if not car_model:
        return {
            "code": 404,
            "message": "车型不存在",
            "data": None
        }
    
    update_data = {
        "name": data.name,
        "brand": data.brand,
        "series": data.series,
        "displacement": data.displacement,
        "year": data.year
    }
    
    updated = await car_model_crud.update(db, db_obj=car_model, obj_in=update_data)
    
    return {
        "code": 0,
        "message": "更新成功",
        "data": updated
    }


@router.delete("/car-model/{car_model_id}")
async def delete_car_model(
    car_model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除车型（软删除）"""
    from app.crud.car_model import car_model_crud
    
    car_model = await car_model_crud.get(db, id=car_model_id)
    if not car_model:
        return {
            "code": 404,
            "message": "车型不存在",
            "data": None
        }
    
    await car_model_crud.delete(db, id=car_model_id)
    
    return {
        "code": 0,
        "message": "删除成功",
        "data": None
    }


@router.get("/car-model/suppliers")
async def get_car_model_suppliers(
    model_name: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """根据车型名称获取供应商列表（用于艾特功能）"""
    from app.crud.car_model import car_model_crud
    
    suppliers = await car_model_crud.get_suppliers_by_model(db, model_name)
    
    return {
        "code": 0,
        "message": "success",
        "data": suppliers
    }
