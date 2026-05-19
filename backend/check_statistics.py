"""
检查 statistics 表中的数据
"""
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from sqlalchemy import text


async def check_statistics():
    """检查 statistics 表数据"""
    async with async_session() as db:
        # 查询总记录数
        result = await db.execute(text("SELECT COUNT(*) as total FROM statistics WHERE is_deleted = 0"))
        total = result.scalar()
        print(f"总记录数: {total}")

        # 查询最近10条记录
        result = await db.execute(
            text("""
                SELECT id, date, vin_code, car_model, source_group, inquirer, quoter, recognize_status, is_quoted
                FROM statistics
                WHERE is_deleted = 0
                ORDER BY date DESC
                LIMIT 10
            """)
        )
        records = result.fetchall()

        if not records:
            print("\n没有数据")
            return

        print("\n最近10条记录:")
        print("-" * 100)
        for r in records:
            print(f"ID: {r.id}")
            print(f"  日期: {r.date}")
            print(f"  车架号: {r.vin_code}")
            print(f"  车型: {r.car_model}")
            print(f"  来源群: {r.source_group}")
            print(f"  询价人: {r.inquirer}")
            print(f"  报价人: {r.quoter}")
            print(f"  识别状态: {r.recognize_status}")
            print(f"  是否报价: {r.is_quoted}")
            print("-" * 100)


if __name__ == "__main__":
    asyncio.run(check_statistics())
