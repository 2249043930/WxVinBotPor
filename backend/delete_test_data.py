"""
删除测试数据
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from sqlalchemy import text


async def delete_test_data():
    """删除测试数据"""
    async with async_session() as db:
        # 删除刚才插入的测试数据 (ID 154, 155, 156)
        result = await db.execute(
            text("DELETE FROM statistics WHERE id IN (154, 155, 156)")
        )
        await db.commit()
        print(f"已删除 {result.rowcount} 条测试数据")

        # 查询验证
        result = await db.execute(
            text("SELECT COUNT(*) as total FROM statistics WHERE is_deleted = 0")
        )
        total = result.scalar()
        print(f"当前 statistics 表记录数: {total}")


if __name__ == "__main__":
    asyncio.run(delete_test_data())
