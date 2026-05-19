from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.group import WechatGroup, WechatGroupCreate, WechatGroupUpdate
from app.services.group_service import GroupService
from app.modules.wxbot.bot import QianxunBot
import httpx
import json

router = APIRouter()


@router.get("/list")
async def get_group_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """请求厂群管理 - 获取微信群列表"""
    service = GroupService(db)
    result = await service.get_list(page, page_size, keyword, is_active)
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.post("/create")
async def create_group(
    group_data: WechatGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建微信群"""
    service = GroupService(db)
    try:
        group = await service.create(group_data)
        return {
            "code": 0,
            "message": "创建成功",
            "data": group
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.put("/update/{group_id}")
async def update_group(
    group_id: int,
    group_data: WechatGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新微信群配置"""
    service = GroupService(db)
    try:
        group = await service.update(group_id, group_data)
        return {
            "code": 0,
            "message": "更新成功",
            "data": group
        }
    except ValueError as e:
        return {
            "code": 1,
            "message": str(e),
            "data": None
        }


@router.delete("/delete/{group_id}")
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除微信群"""
    service = GroupService(db)
    try:
        await service.delete(group_id)
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


@router.put("/status/{group_id}")
async def update_group_status(
    group_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新微信群状态（启用/禁用）"""
    from app.crud.group import group_crud
    
    group = await group_crud.get(db, id=group_id)
    if not group:
        return {
            "code": 1,
            "message": "群不存在",
            "data": None
        }
    
    # 获取状态值（支持 status 或 is_active 参数名）
    is_active = status_data.get("is_active") if "is_active" in status_data else status_data.get("status")
    if is_active is None:
        return {
            "code": 1,
            "message": "缺少status或is_active参数",
            "data": None
        }
    
    # 将 status 转换为布尔值
    if isinstance(is_active, (int, float)):
        is_active = bool(is_active)
    elif isinstance(is_active, str):
        is_active = is_active.lower() in ('true', '1', 'yes', 'on')
    
    # 更新状态
    update_data = {"is_active": is_active}
    updated_group = await group_crud.update(db, db_obj=group, obj_in=update_data)
    
    # 同步更新机器人监听列表
    from app.modules.wxbot.bot_manager import get_bot_manager
    bot_manager = get_bot_manager()
    if bot_manager.websocket_client:
        if is_active:
            bot_manager.add_group(updated_group.group_id)
        else:
            bot_manager.remove_group(updated_group.group_id)
    
    return {
        "code": 0,
        "message": "状态更新成功",
        "data": {
            "id": updated_group.id,
            "group_id": updated_group.group_id,
            "group_name": updated_group.group_name,
            "is_active": updated_group.is_active
        }
    }


@router.get("/members/{group_wxid}")
async def get_group_members(
    group_wxid: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取群成员列表 - 群聊成员获取"""
    service = GroupService(db)
    result = await service.get_members(group_wxid)
    return {
        "code": 0,
        "message": "success",
        "data": result
    }


@router.post("/sync")
async def sync_groups_from_wechat(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """从微信自动同步群聊列表"""
    try:
        # 调用千寻por API获取微信群聊列表
        bot = QianxunBot()
        groups_data = await fetch_wechat_groups(bot)
        
        service = GroupService(db)
        result = await service.sync_groups(groups_data)
        
        return {
            "code": 0,
            "message": f"成功同步 {len(result)} 个群聊",
            "data": {
                "synced_count": len(result),
                "groups": result
            }
        }
    except Exception as e:
        return {
            "code": 1,
            "message": f"同步失败: {str(e)}",
            "data": None
        }


@router.get("/notification/{group_id}")
async def get_group_notification(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取群通知配置"""
    from app.crud.group import group_crud
    import json

    group = await group_crud.get(db, id=group_id)
    if not group:
        return {
            "code": 1,
            "message": "群不存在",
            "data": None
        }

    # 解析关键词配置
    keywords_config = {
        "quote_keywords": [],
        "delivery_keywords": [],
        "deal_keywords": []
    }
    if group.notify_keywords:
        try:
            keywords_config = json.loads(group.notify_keywords)
        except:
            pass

    return {
        "code": 0,
        "message": "success",
        "data": {
            "inquiry_notify": group.inquiry_notify,
            "quote_notify": group.quote_notify,
            "delivery_notify": group.delivery_notify,
            "deal_notify": group.deal_notify,
            "work_start_time": group.work_start_time.strftime("%H:%M") if group.work_start_time else None,
            "work_end_time": group.work_end_time.strftime("%H:%M") if group.work_end_time else None,
            "notify_keywords": group.notify_keywords,
            "keywords_config": keywords_config
        }
    }


@router.put("/notification/{group_id}")
async def update_group_notification(
    group_id: int,
    notification_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新群通知配置"""
    from app.crud.group import group_crud
    import json

    group = await group_crud.get(db, id=group_id)
    if not group:
        return {
            "code": 1,
            "message": "群不存在",
            "data": None
        }

    # 更新通知配置
    update_data = {
        "inquiry_notify": notification_data.get("inquiry_notify", group.inquiry_notify),
        "quote_notify": notification_data.get("quote_notify", group.quote_notify),
        "delivery_notify": notification_data.get("delivery_notify", group.delivery_notify),
        "deal_notify": notification_data.get("deal_notify", group.deal_notify),
    }

    # 处理关键词配置
    if "keywords_config" in notification_data:
        try:
            keywords_config = notification_data["keywords_config"]
            update_data["notify_keywords"] = json.dumps(keywords_config, ensure_ascii=False)
        except:
            pass
    elif "notify_keywords" in notification_data:
        update_data["notify_keywords"] = notification_data["notify_keywords"]

    # 处理时间字段
    from datetime import datetime, time
    if "work_start_time" in notification_data and notification_data["work_start_time"]:
        try:
            if isinstance(notification_data["work_start_time"], str):
                t = datetime.strptime(notification_data["work_start_time"], "%H:%M").time()
                update_data["work_start_time"] = t
        except:
            pass

    if "work_end_time" in notification_data and notification_data["work_end_time"]:
        try:
            if isinstance(notification_data["work_end_time"], str):
                t = datetime.strptime(notification_data["work_end_time"], "%H:%M").time()
                update_data["work_end_time"] = t
        except:
            pass

    updated_group = await group_crud.update(db, db_obj=group, obj_in=update_data)

    # 解析关键词配置用于返回
    keywords_config = {
        "quote_keywords": [],
        "delivery_keywords": [],
        "deal_keywords": []
    }
    if updated_group.notify_keywords:
        try:
            keywords_config = json.loads(updated_group.notify_keywords)
        except:
            pass

    return {
        "code": 0,
        "message": "更新成功",
        "data": {
            "inquiry_notify": updated_group.inquiry_notify,
            "quote_notify": updated_group.quote_notify,
            "delivery_notify": updated_group.delivery_notify,
            "deal_notify": updated_group.deal_notify,
            "work_start_time": updated_group.work_start_time.strftime("%H:%M") if updated_group.work_start_time else None,
            "work_end_time": updated_group.work_end_time.strftime("%H:%M") if updated_group.work_end_time else None,
            "notify_keywords": updated_group.notify_keywords,
            "keywords_config": keywords_config
        }
    }


async def fetch_wechat_groups(bot: QianxunBot) -> list:
    """从千寻por API获取微信群聊列表"""
    async with httpx.AsyncClient() as client:
        payload = {
            "type": "getGroupList",
            "data": {
                "type": "1"
            }
        }
        
        response = await client.post(
            f"{bot.api_base}/qianxun/httpapi?wxid={bot.wx_id}&safekey=",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        
        data = response.json()
        print(f"API Response: {data}")
        
        # 千寻por API返回的数据在 result 字段中
        if "result" not in data:
            raise Exception(f"获取群聊列表失败: {data.get('msg', '未知错误')}")
        
        groups = []
        for group in data["result"]:
            groups.append({
                "group_id": group.get("wxid", ""),
                "group_name": group.get("nick", ""),
                "member_count": int(group.get("groupMemberNum", 0)),
                "remark": group.get("remark", "")
            })
        
        return groups
