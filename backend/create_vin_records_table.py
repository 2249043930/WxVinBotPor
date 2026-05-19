"""
创建 vin_records 表
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.models.vin_record import VinRecord
from sqlalchemy import inspect


async def create_table():
    """创建 vin_records 表"""
    async with engine.begin() as conn:
        # 检查表是否存在
        def check_table_exists(connection):
            inspector = inspect(connection)
            return inspector.has_table("vin_records")

        result = await conn.run_sync(check_table_exists)

        if result:
            print("vin_records 表已存在")
        else:
            # 创建表
            await conn.run_sync(VinRecord.__table__.create)
            print("vin_records 表创建成功")


if __name__ == "__main__":
    asyncio.run(create_table())
