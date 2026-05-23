"""
群成员CRUD操作
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.crud.base import CRUDBase
from app.models.group_member import GroupMember


class CRUDGroupMember(CRUDBase[GroupMember]):
    """群成员CRUD"""

    async def get_by_group_and_wxid(
        self, 
        db: AsyncSession, 
        group_id: str, 
        wxid: str
    ) -> Optional[GroupMember]:
        """通过群ID和wxid获取成员"""
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.wxid == wxid
            )
        )
        return result.scalar_one_or_none()

    async def get_by_group_id(
        self, 
        db: AsyncSession, 
        group_id: str
    ) -> List[GroupMember]:
        """获取群的所有成员"""
        result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        return result.scalars().all()

    async def get_by_wxid(
        self, 
        db: AsyncSession, 
        wxid: str
    ) -> List[GroupMember]:
        """获取某个wxid在所有群中的记录"""
        result = await db.execute(
            select(GroupMember).where(GroupMember.wxid == wxid)
        )
        return result.scalars().all()

    async def sync_members(
        self,
        db: AsyncSession,
        group_id: str,
        members: List[dict]
    ) -> dict:
        """同步群成员
        
        Args:
            db: 数据库会话
            group_id: 群ID
            members: 成员列表 [{"wxid": "...", "nick": "...", "group_nick": "..."}]
            
        Returns:
            dict: 同步结果统计
        """
        # 获取现有成员
        existing_members = await self.get_by_group_id(db, group_id)
        existing_wxids = {m.wxid for m in existing_members}
        new_wxids = {m["wxid"] for m in members}
        
        # 删除已不在群中的成员
        removed_wxids = existing_wxids - new_wxids
        if removed_wxids:
            await db.execute(
                delete(GroupMember).where(
                    GroupMember.group_id == group_id,
                    GroupMember.wxid.in_(removed_wxids)
                )
            )
        
        # 添加或更新成员
        added_count = 0
        updated_count = 0
        
        for member_data in members:
            wxid = member_data["wxid"]
            existing = await self.get_by_group_and_wxid(db, group_id, wxid)
            
            if existing:
                # 更新现有成员
                existing.nick = member_data.get("nick") or existing.nick
                existing.group_nick = member_data.get("group_nick") or existing.group_nick
                updated_count += 1
            else:
                # 创建新成员
                new_member = GroupMember(
                    group_id=group_id,
                    wxid=wxid,
                    nick=member_data.get("nick"),
                    group_nick=member_data.get("group_nick")
                )
                db.add(new_member)
                added_count += 1
        
        await db.commit()
        
        return {
            "added": added_count,
            "updated": updated_count,
            "removed": len(removed_wxids),
            "total": len(members)
        }

    async def find_groups_by_supplier_wxid(
        self,
        db: AsyncSession,
        supplier_wxid: str,
        exclude_group_id: Optional[str] = None
    ) -> List[GroupMember]:
        """查找包含特定供应商的所有群
        
        Args:
            db: 数据库会话
            supplier_wxid: 供应商wxid
            exclude_group_id: 排除的群ID（通常是源群）
            
        Returns:
            List[GroupMember]: 群成员记录列表
        """
        query = select(GroupMember).where(GroupMember.wxid == supplier_wxid)
        
        if exclude_group_id:
            query = query.where(GroupMember.group_id != exclude_group_id)
        
        result = await db.execute(query)
        return result.scalars().all()


# 创建实例
group_member_crud = CRUDGroupMember(GroupMember)
