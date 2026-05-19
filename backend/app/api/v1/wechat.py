"""
微信账号管理 API
提供微信账号的绑定、解绑、查询等功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud.user import user_crud
from app.models.user import User

router = APIRouter()


class WechatAccountResponse(BaseModel):
    """微信账号响应"""
    id: int
    wxid: str
    nickname: str
    avatar: Optional[str] = None
    status: int  # 1: 已绑定, 0: 已解绑
    bind_time: Optional[str] = None


class WechatBindRequest(BaseModel):
    """微信绑定请求"""
    wxid: str
    nickname: Optional[str] = None


class WechatUnbindRequest(BaseModel):
    """微信解绑请求"""
    user_id: int


@router.get("/list")
async def get_wechat_list(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取微信账号列表"""
    try:
        # 查询所有用户
        users = await user_crud.get_multi(
            db,
            skip=(page - 1) * page_size,
            limit=page_size
        )
        
        # 过滤出有微信ID的用户
        wechat_accounts = []
        for user in users:
            if user.wx_id:  # 只返回有微信ID的用户
                wechat_accounts.append({
                    "id": user.id,
                    "wxid": user.wx_id,
                    "nickname": user.nickname or user.wx_id,
                    "avatar": "",  # 头像字段，暂时为空
                    "status": 1 if user.is_active else 0,
                    "bind_time": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
                })
        
        # 获取总数
        total = len(wechat_accounts)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "list": wechat_accounts,
                "total": total
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"获取列表失败: {str(e)}",
            "data": None
        }


@router.post("/bind")
async def bind_wechat(
    request: WechatBindRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """绑定微信账号"""
    try:
        # 检查 wxid 是否已被绑定
        existing_user = await user_crud.get_by_wx_id(db, request.wxid)
        if existing_user:
            return {
                "code": 1,
                "message": "该微信账号已被绑定",
                "data": None
            }
        
        # 更新当前用户的微信ID
        user = await user_crud.get(db, id=current_user.id)
        if not user:
            return {
                "code": 1,
                "message": "用户不存在",
                "data": None
            }
        
        user.wx_id = request.wxid
        if request.nickname:
            user.nickname = request.nickname
            
        await db.commit()
        await db.refresh(user)
        
        return {
            "code": 0,
            "message": "绑定成功",
            "data": {
                "id": user.id,
                "wxid": user.wx_id,
                "nickname": user.nickname
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"绑定失败: {str(e)}",
            "data": None
        }


@router.post("/unbind/{user_id}")
async def unbind_wechat(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """解绑微信账号"""
    try:
        # 获取用户
        user = await user_crud.get(db, id=user_id)
        if not user:
            return {
                "code": 1,
                "message": "用户不存在",
                "data": None
            }
        
        # 清空微信ID
        user.wx_id = None
        user.wx_group_name = None
        user.group_member_wxid = None
        
        await db.commit()
        await db.refresh(user)
        
        return {
            "code": 0,
            "message": "解绑成功",
            "data": {
                "id": user.id,
                "wxid": None
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"解绑失败: {str(e)}",
            "data": None
        }


@router.post("/refresh/{user_id}")
async def refresh_wechat(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """刷新微信账号信息"""
    try:
        # 获取用户
        user = await user_crud.get(db, id=user_id)
        if not user:
            return {
                "code": 1,
                "message": "用户不存在",
                "data": None
            }
        
        # TODO: 调用千寻框架 API 获取最新的微信信息
        # 这里只是返回当前信息
        
        return {
            "code": 0,
            "message": "刷新成功",
            "data": {
                "id": user.id,
                "wxid": user.wx_id,
                "nickname": user.nickname,
                "status": 1 if user.is_active else 0
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"刷新失败: {str(e)}",
            "data": None
        }


@router.get("/detail/{user_id}")
async def get_wechat_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取微信账号详情"""
    try:
        user = await user_crud.get(db, id=user_id)
        if not user:
            return {
                "code": 1,
                "message": "用户不存在",
                "data": None
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "id": user.id,
                "wxid": user.wx_id,
                "nickname": user.nickname,
                "wx_group_name": user.wx_group_name,
                "group_member_wxid": user.group_member_wxid,
                "status": 1 if user.is_active else 0,
                "bind_time": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"获取详情失败: {str(e)}",
            "data": None
        }
