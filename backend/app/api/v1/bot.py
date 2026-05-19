"""
微信机器人管理 API
提供群聊监听服务的启动、停止、状态查询等接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.modules.wxbot.bot_manager import BotManager, get_bot_manager, start_bot_manager, stop_bot_manager

router = APIRouter()


class BotStatusResponse(BaseModel):
    """机器人状态响应"""
    is_running: bool
    monitored_groups: List[str]
    wx_id: str
    websocket_uri: str


class GroupMonitorRequest(BaseModel):
    """群聊监听请求"""
    group_ids: List[str]


@router.get("/status")
async def get_bot_status(
    current_user = Depends(get_current_user)
):
    """获取机器人状态"""
    manager = get_bot_manager()
    status = manager.get_status()
    
    return {
        "code": 0,
        "message": "success",
        "data": status
    }


@router.post("/start")
async def start_bot(
    current_user = Depends(get_current_user)
):
    """启动群聊监听服务"""
    try:
        manager = get_bot_manager()
        
        if manager.is_running:
            return {
                "code": 1,
                "message": "监听服务已在运行",
                "data": manager.get_status()
            }
        
        # 启动机器人管理器
        await manager.start()
        
        return {
            "code": 0,
            "message": "监听服务启动成功",
            "data": manager.get_status()
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"启动失败: {str(e)}",
            "data": None
        }


@router.post("/stop")
async def stop_bot(
    current_user = Depends(get_current_user)
):
    """停止群聊监听服务"""
    try:
        manager = get_bot_manager()
        await manager.stop()
            
        return {
            "code": 0,
            "message": "监听服务已停止",
            "data": None
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"停止失败: {str(e)}",
            "data": None
        }


@router.post("/groups/add")
async def add_monitored_groups(
    request: GroupMonitorRequest,
    current_user = Depends(get_current_user)
):
    """添加监听的群聊"""
    try:
        manager = get_bot_manager()
        
        if not manager.is_running:
            return {
                "code": 1,
                "message": "监听服务未启动",
                "data": None
            }
        
        for group_id in request.group_ids:
            manager.add_group(group_id)
            
        return {
            "code": 0,
            "message": f"已添加 {len(request.group_ids)} 个群聊到监听列表",
            "data": {
                "monitored_groups": list(manager.websocket_client.monitored_groups)
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"添加失败: {str(e)}",
            "data": None
        }


@router.post("/groups/remove")
async def remove_monitored_groups(
    request: GroupMonitorRequest,
    current_user = Depends(get_current_user)
):
    """移除监听的群聊"""
    try:
        manager = get_bot_manager()
        
        if not manager.is_running:
            return {
                "code": 1,
                "message": "监听服务未启动",
                "data": None
            }
        
        for group_id in request.group_ids:
            manager.remove_group(group_id)
            
        return {
            "code": 0,
            "message": f"已移除 {len(request.group_ids)} 个群聊从监听列表",
            "data": {
                "monitored_groups": list(manager.websocket_client.monitored_groups)
            }
        }
        
    except Exception as e:
        return {
            "code": 1,
            "message": f"移除失败: {str(e)}",
            "data": None
        }


@router.get("/groups/monitored")
async def get_monitored_groups(
    current_user = Depends(get_current_user)
):
    """获取当前监听的群聊列表"""
    manager = get_bot_manager()
    status = manager.get_status()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "monitored_groups": status["monitored_groups"],
            "is_running": status["is_running"]
        }
    }
