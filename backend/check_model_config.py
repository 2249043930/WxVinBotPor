"""
检查数据库中的模型配置
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_config():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 检查 API 配置表结构 ===')
        result = await db.execute(text("""
            SHOW COLUMNS FROM api_configs
        """))
        columns = result.fetchall()
        print("表字段:")
        for col in columns:
            print(f"  - {col.Field} ({col.Type})")
        
        print('\n=== 检查 API 配置数据 ===')
        result = await db.execute(text("""
            SELECT * FROM api_configs
        """))
        configs = result.fetchall()
        
        if not configs:
            print('没有找到API配置')
            return
        
        for c in configs:
            print(f"\n配置: {c}")

if __name__ == '__main__':
    asyncio.run(check_config())
