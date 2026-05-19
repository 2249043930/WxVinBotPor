from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.group import group_crud
from app.schemas.group import WechatGroup, WechatGroupCreate, WechatGroupUpdate


class GroupService:
    """厂群管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ):
        """获取群列表"""
        skip = (page - 1) * page_size
        groups, total = await group_crud.search_groups(
            self.db,
            keyword=keyword,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )

        return {
            "list": groups,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def create(self, group_data: WechatGroupCreate) -> WechatGroup:
        """创建群"""
        # 检查group_id是否已存在
        existing = await group_crud.get_by_group_id(self.db, group_data.group_id)
        if existing:
            raise ValueError("群ID已存在")

        group_dict = group_data.model_dump()
        return await group_crud.create(self.db, obj_in=group_dict)

    async def update(self, group_id: int, group_data: WechatGroupUpdate) -> WechatGroup:
        """更新群"""
        group = await group_crud.get(self.db, id=group_id)
        if not group:
            raise ValueError("群不存在")

        update_dict = group_data.model_dump(exclude_unset=True)
        return await group_crud.update(self.db, db_obj=group, obj_in=update_dict)

    async def delete(self, group_id: int):
        """删除群"""
        group = await group_crud.get(self.db, id=group_id)
        if not group:
            raise ValueError("群不存在")

        await group_crud.delete(self.db, id=group_id)

    async def get_members(self, group_wxid: str) -> List[dict]:
        """获取群成员列表 - 从千寻机器人API获取真实数据"""
        from app.modules.wxbot.bot import QianxunBot
        from loguru import logger
        
        try:
            bot = QianxunBot()
            members = await bot.get_group_members(group_wxid)
            
            # 格式化成员数据
            result = []
            for member in members:
                wxid = member.get("wxid", "")
                nick = member.get("nick", "")
                group_nick = member.get("groupNick", "")
                
                # 跳过机器人自己
                if wxid == bot.wx_id:
                    continue
                
                result.append({
                    "wxid": wxid,
                    "nick": nick or group_nick,
                    "group_nick": group_nick,
                    "display_name": f"{group_nick or nick} ({wxid})" if (group_nick or nick) else wxid
                })
            
            logger.info(f"从千寻API获取群成员成功: {group_wxid}, 共 {len(result)} 人")
            return result
            
        except Exception as e:
            logger.error(f"从千寻API获取群成员失败: {e}")
            # 失败时返回空列表，让调用方处理
            return []

    async def sync_groups(self, groups_data: list) -> list:
        """同步微信群聊到数据库
        
        Args:
            groups_data: 从微信获取的群聊列表
            
        Returns:
            list: 同步成功的群聊列表
        """
        from app.models.group import WechatGroup as WechatGroupModel
        
        synced_groups = []
        
        for group_data in groups_data:
            # 检查群是否已存在
            existing = await group_crud.get_by_group_id(self.db, group_data["group_id"])
            
            if existing:
                # 更新现有群信息
                update_data = {
                    "group_name": group_data["group_name"],
                    "member_count": group_data["member_count"]
                }
                await group_crud.update(self.db, db_obj=existing, obj_in=update_data)
                synced_groups.append({
                    "id": existing.id,
                    "group_id": existing.group_id,
                    "group_name": existing.group_name,
                    "action": "updated"
                })
            else:
                # 创建新群
                new_group_data = {
                    "group_name": group_data["group_name"],
                    "group_id": group_data["group_id"],
                    "member_count": group_data["member_count"],
                    "is_active": True,
                    "inquiry_notify": True,
                    "quote_notify": True,
                    "delivery_notify": True,
                    "deal_notify": True
                }
                new_group = await group_crud.create(self.db, obj_in=new_group_data)
                synced_groups.append({
                    "id": new_group.id,
                    "group_id": new_group.group_id,
                    "group_name": new_group.group_name,
                    "action": "created"
                })
        
        await self.db.commit()
        return synced_groups
