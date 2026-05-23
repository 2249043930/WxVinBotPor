"""
手动同步所有群成员到数据库
"""
import asyncio
import sys
sys.path.insert(0, 'd:\\Client Projects\\WxVinBot Por\\backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import settings
from app.modules.wxbot.bot import QianxunBot
from app.crud.group_member import group_member_crud

async def sync_all_members():
    """同步所有群的成员"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # 获取所有群
        result = await db.execute(text('SELECT group_id, group_name FROM wechat_groups'))
        groups = result.fetchall()
        
        print(f'共找到 {len(groups)} 个群')
        
        bot = QianxunBot()
        
        success_count = 0
        fail_count = 0
        
        for i, group in enumerate(groups, 1):
            print(f'\n[{i}/{len(groups)}] 同步群: {group.group_name} ({group.group_id})')
            
            try:
                # 从千寻API获取成员
                members = await bot.get_group_members(group.group_id)
                
                if not members:
                    print(f'  ⚠️ 获取成员为空')
                    fail_count += 1
                    continue
                
                print(f'  ✓ 获取到 {len(members)} 个成员')
                
                # 同步到数据库
                result = await group_member_crud.sync_members(db, group.group_id, members)
                print(f'  ✓ 同步完成: 新增{result["added"]}人, 更新{result["updated"]}人, 删除{result["removed"]}人')
                success_count += 1
                
            except Exception as e:
                print(f'  ✗ 同步失败: {e}')
                fail_count += 1
        
        print(f'\n\n同步完成: 成功{success_count}个群, 失败{fail_count}个群')

if __name__ == '__main__':
    asyncio.run(sync_all_members())
