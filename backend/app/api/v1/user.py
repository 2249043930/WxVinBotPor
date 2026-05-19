from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from app.services.user_service import UserService

router = APIRouter()


class StatusUpdateRequest(BaseModel):
    status: int


@router.get("/list")
async def get_user_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求系统管理 - 获取用户列表"""
    service = UserService(db)
    result = await service.get_list(page, page_size, keyword, is_active)
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.post("/create")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建用户"""
    service = UserService(db)
    try:
        user = await service.create(user_data)
        return {
            "code": 0,
            "message": "创建成功",
            "data": user
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.put("/update/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新用户"""
    service = UserService(db)
    try:
        user = await service.update(user_id, user_data)
        return {
            "code": 0,
            "message": "更新成功",
            "data": user
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除用户"""
    service = UserService(db)
    try:
        await service.delete(user_id)
        return {
            "code": 0,
            "message": "删除成功",
            "data": None
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.put("/status/{user_id}")
async def toggle_user_status(
    user_id: int,
    data: StatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """切换用户状态"""
    service = UserService(db)
    try:
        from app.schemas.user import UserUpdate
        user_data = UserUpdate(is_active=bool(data.status))
        user = await service.update(user_id, user_data)
        return {
            "code": 0,
            "message": "状态更新成功",
            "data": user
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.post("/reset-password/{user_id}")
async def reset_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """重置密码"""
    service = UserService(db)
    try:
        await service.reset_password(user_id, new_password)
        return {
            "code": 0,
            "message": "密码重置成功",
            "data": None
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }
