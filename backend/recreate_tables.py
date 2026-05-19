"""
重新创建数据库表脚本
用于在模型变更后更新表结构
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models.base import Base

async def recreate_tables():
    """删除并重新创建所有表"""
    # 创建引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # 删除所有表
        print("正在删除旧表...")
        await conn.run_sync(Base.metadata.drop_all)
        print("旧表已删除")
        
        # 创建所有表
        print("正在创建新表...")
        await conn.run_sync(Base.metadata.create_all)
        print("新表已创建")
    
    await engine.dispose()
    print("完成！")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
