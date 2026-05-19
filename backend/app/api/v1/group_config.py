"""
群聊配置API
管理每个群聊的客服配置和车型-供应商绑定
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.session import get_db
from app.core.security import get_current_user
from app.crud.group_config import group_config_crud
from app.crud.group import group_crud
from app.crud.car_model import car_model_crud
from app.models.group_config import GroupConfig, GroupModelSupplier
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from loguru import logger

router = APIRouter()


@router.get("/groups")
async def get_groups_for_config(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取可用于配置的群聊列表（从群管理模块同步）"""
    groups = await group_crud.get_active_groups(db)
    return {
        "code": 0,
        "message": "success",
        "data": [
            {
                "group_id": g.group_id,
                "group_name": g.group_name
            }
            for g in groups
        ]
    }


@router.get("/list")
async def get_group_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取群聊配置列表"""
    skip = (page - 1) * page_size
    configs = await group_config_crud.get_multi(db, skip=skip, limit=page_size)
    
    # 获取总数
    from sqlalchemy import select, func
    result = await db.execute(select(func.count(GroupConfig.id)))
    total = result.scalar() or 0
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "list": [config.to_dict() for config in configs],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/detail/{group_id}")
async def get_group_config_detail(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个群聊配置详情"""
    config = await group_config_crud.get_by_group_id(db, group_id=group_id)
    if not config:
        # 配置不存在时返回空数据，不显示错误
        return {
            "code": 0,
            "message": "success",
            "data": None
        }
    
    return {
        "code": 0,
        "message": "success",
        "data": config.to_dict()
    }


@router.post("/create")
async def create_group_config(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建群聊配置（如果已存在则自动更新）"""
    from app.crud.supplier import supplier_crud
    
    # 检查是否已存在（不加载关系，避免会话问题）
    existing = await group_config_crud.get_by_group_id(db, group_id=data.get("group_id"), load_relations=False)
    
    # 处理供应商绑定 - 根据wxid查找或创建供应商
    model_suppliers = data.get("model_suppliers", [])
    processed_suppliers = []
    
    for ms in model_suppliers:
        supplier_wxid = ms.get("supplier_wxid")
        supplier_name = ms.get("supplier_name", "")
        
        if supplier_wxid:
            # 根据wxid查找供应商
            supplier = await supplier_crud.get_by_wxid(db, supplier_wxid)
            
            if not supplier:
                # 供应商不存在，创建新供应商
                try:
                    supplier = await supplier_crud.create(db, obj_in={
                        "wxid": supplier_wxid,
                        "name": supplier_name or supplier_wxid,
                        "member_type_id": 1  # 默认类型
                    })
                    logger.info(f"创建新供应商: {supplier_name} ({supplier_wxid})")
                except Exception as e:
                    logger.error(f"创建供应商失败: {e}")
                    continue
            
            processed_suppliers.append({
                "car_model_id": ms["car_model_id"],
                "supplier_id": supplier.id
            })
    
    if existing:
        # 已存在配置，自动转为更新
        logger.info(f"群聊 {data.get('group_id')} 已存在配置，自动转为更新")
        config = await group_config_crud.update_with_models(
            db,
            config_id=existing.id,
            group_name=data.get("group_name"),
            customer_service_wxid=data.get("customer_service_wxid"),
            customer_service_name=data.get("customer_service_name"),
            model_suppliers=processed_suppliers
        )
        
        if not config:
            return {
                "code": 404,
                "message": "配置不存在",
                "data": None
            }
        
        # 预加载关系数据
        result = await db.execute(
            select(GroupConfig)
            .where(GroupConfig.id == existing.id)
            .options(
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model),
                selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier)
            )
        )
        config_with_relations = result.scalar_one()
        
        return {
            "code": 0,
            "message": "配置更新成功",
            "data": config_with_relations.to_dict()
        }
    
    # 不存在配置，创建新配置
    config = await group_config_crud.create_with_models(
        db,
        group_id=data.get("group_id"),
        group_name=data.get("group_name"),
        customer_service_wxid=data.get("customer_service_wxid"),
        customer_service_name=data.get("customer_service_name"),
        model_suppliers=processed_suppliers
    )
    
    return {
        "code": 0,
        "message": "配置创建成功",
        "data": config.to_dict()
    }


@router.put("/update/{config_id}")
async def update_group_config(
    config_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新群聊配置"""
    from app.crud.supplier import supplier_crud
    
    # 处理供应商绑定 - 根据wxid查找或创建供应商
    model_suppliers = data.get("model_suppliers", [])
    processed_suppliers = []
    
    for ms in model_suppliers:
        supplier_wxid = ms.get("supplier_wxid")
        supplier_name = ms.get("supplier_name", "")
        
        if supplier_wxid:
            # 根据wxid查找供应商
            supplier = await supplier_crud.get_by_wxid(db, supplier_wxid)
            
            if not supplier:
                # 供应商不存在，创建新供应商
                try:
                    supplier = await supplier_crud.create(db, obj_in={
                        "wxid": supplier_wxid,
                        "name": supplier_name or supplier_wxid,
                        "member_type_id": 1  # 默认类型
                    })
                    logger.info(f"更新时创建新供应商: {supplier_name} ({supplier_wxid})")
                except Exception as e:
                    logger.error(f"更新时创建供应商失败: {e}")
                    continue
            
            processed_suppliers.append({
                "car_model_id": ms["car_model_id"],
                "supplier_id": supplier.id
            })
    
    config = await group_config_crud.update_with_models(
        db,
        config_id=config_id,
        group_name=data.get("group_name"),
        customer_service_wxid=data.get("customer_service_wxid"),
        customer_service_name=data.get("customer_service_name"),
        model_suppliers=processed_suppliers
    )
    
    if not config:
        return {
            "code": 404,
            "message": "配置不存在",
            "data": None
        }
    
    # 预加载关系数据，避免在会话关闭后访问
    result = await db.execute(
        select(GroupConfig)
        .where(GroupConfig.id == config.id)
        .options(
            selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.car_model),
            selectinload(GroupConfig.model_suppliers).selectinload(GroupModelSupplier.supplier)
        )
    )
    config_with_relations = result.scalar_one()
    
    return {
        "code": 0,
        "message": "更新成功",
        "data": config_with_relations.to_dict()
    }


@router.delete("/delete/{config_id}")
async def delete_group_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除群聊配置"""
    config = await group_config_crud.get(db, id=config_id)
    if not config:
        return {
            "code": 404,
            "message": "配置不存在",
            "data": None
        }
    
    await group_config_crud.delete(db, id=config_id)
    
    return {
        "code": 0,
        "message": "删除成功",
        "data": None
    }


@router.get("/suppliers-by-model")
async def get_suppliers_by_model(
    group_id: str,
    car_model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取群中某个车型的供应商"""
    model_supplier = await group_config_crud.get_supplier_by_model(
        db, group_id=group_id, car_model_id=car_model_id
    )
    
    if not model_supplier:
        return {
            "code": 404,
            "message": "未找到该车型绑定的供应商",
            "data": None
        }
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "supplier_wxid": model_supplier.supplier.wxid if model_supplier.supplier else None,
            "supplier_name": model_supplier.supplier.name if model_supplier.supplier else None
        }
    }


@router.get("/group-members")
async def get_group_members(
    group_id: str,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取群成员列表，支持模糊搜索 - 优先从千寻API获取真实数据"""
    try:
        result = []
        api_success = False
        
        # 方法1: 尝试从机器人管理器获取（如果已启动）
        try:
            from app.modules.wxbot.bot_manager import get_bot_manager
            bot_manager = get_bot_manager()
            
            logger.info(f"尝试从机器人管理器获取群成员: group_id={group_id}")
            if bot_manager and bot_manager.bot:
                members = await bot_manager.bot.get_group_members(group_id)
                logger.info(f"机器人管理器返回成员数量: {len(members)}")
                
                if members:
                    for member in members:
                        wxid = member.get("wxid", "")
                        nick = member.get("nick", "")
                        group_nick = member.get("groupNick", "")
                        
                        # 跳过机器人自己
                        if wxid == bot_manager.bot.wx_id:
                            continue
                        
                        result.append({
                            "wxid": wxid,
                            "nick": nick or group_nick,
                            "group_nick": group_nick,
                            "display_name": f"{group_nick or nick} ({wxid})" if (group_nick or nick) else wxid
                        })
                    api_success = True
                    logger.info(f"从机器人管理器获取到 {len(result)} 个成员")
        except Exception as e:
            logger.warning(f"从机器人管理器获取群成员失败: {e}")
        
        # 方法2: 如果方法1失败，直接调用千寻API
        if not api_success:
            try:
                from app.modules.wxbot.bot import QianxunBot
                logger.info(f"尝试直接调用千寻API获取群成员: group_id={group_id}")
                
                bot = QianxunBot()
                members = await bot.get_group_members(group_id)
                logger.info(f"千寻API返回成员数量: {len(members)}")
                
                if members:
                    for member in members:
                        wxid = member.get("wxid", "")
                        nick = member.get("nick", "")
                        group_nick = member.get("groupNick", "")
                        
                        # 跳过机器人自己
                        if wxid == bot.wx_id:
                            continue
                        
                        # 如果groupNick为空，尝试调用API获取
                        if not group_nick and wxid:
                            try:
                                group_nick = await bot.get_member_nick(group_id, wxid)
                                logger.debug(f"获取到成员 {wxid} 的群昵称: {group_nick}")
                            except Exception as e:
                                logger.debug(f"获取成员 {wxid} 昵称失败: {e}")
                        
                        # 构建显示名称
                        display_nick = group_nick or nick or ""
                        if display_nick:
                            display_name = f"{display_nick} ({wxid})"
                        else:
                            display_name = wxid
                        
                        result.append({
                            "wxid": wxid,
                            "nick": nick or group_nick,
                            "group_nick": group_nick,
                            "display_name": display_name
                        })
                    api_success = True
                    logger.info(f"从千寻API直接获取到 {len(result)} 个成员")
            except Exception as e:
                logger.warning(f"直接调用千寻API获取群成员失败: {e}")
        
        # 方法3: 如果API都失败，从数据库获取备选数据
        if not result:
            logger.info(f"API获取失败，尝试从数据库获取备选数据: group_id={group_id}")
            
            from app.crud.group_config import group_config_crud
            from app.crud.supplier import supplier_crud
            
            # 获取群聊配置中的客服和供应商
            config = await group_config_crud.get_by_group_id(db, group_id)
            if config:
                # 添加客服
                if config.customer_service_wxid:
                    result.append({
                        "wxid": config.customer_service_wxid,
                        "nick": config.customer_service_name or "客服",
                        "group_nick": config.customer_service_name or "客服",
                        "display_name": f"{config.customer_service_name or '客服'} ({config.customer_service_wxid})"
                    })
                
                # 添加已配置的供应商
                for ms in config.model_suppliers:
                    if ms.supplier:
                        result.append({
                            "wxid": ms.supplier.wxid,
                            "nick": ms.supplier.name,
                            "group_nick": ms.supplier.name,
                            "display_name": f"{ms.supplier.name} ({ms.supplier.wxid})"
                        })
            
            # 获取所有供应商作为备选
            suppliers = await supplier_crud.get_multi(db, skip=0, limit=100)
            for supplier in suppliers:
                # 去重
                if not any(r["wxid"] == supplier.wxid for r in result):
                    result.append({
                        "wxid": supplier.wxid,
                        "nick": supplier.name,
                        "group_nick": supplier.name,
                        "display_name": f"{supplier.name} ({supplier.wxid})"
                    })
            
            logger.info(f"从数据库获取到 {len(result)} 个备选成员")
        
        # 模糊搜索过滤
        if keyword and result:
            keyword_lower = keyword.lower()
            filtered_result = [r for r in result if 
                     keyword_lower in (r.get("nick") or "").lower() or 
                     keyword_lower in (r.get("group_nick") or "").lower() or
                     keyword_lower in r.get("wxid", "").lower()]
            # 如果搜索有结果，使用搜索结果；否则返回全部
            if filtered_result:
                result = filtered_result
                logger.info(f"关键词 '{keyword}' 过滤后剩余 {len(result)} 个成员")
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"获取群成员失败: {e}")
        return {
            "code": 500,
            "message": f"获取群成员失败: {str(e)}",
            "data": []
        }
