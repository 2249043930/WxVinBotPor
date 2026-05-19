"""
检查所有相关表的数据
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from sqlalchemy import text


async def check_all_tables():
    """检查所有相关表数据"""
    async with async_session() as db:
        tables = [
            "statistics",
            "message_records",
            "vin_info",
            "vin_records",
            "wechat_groups",
            "group_configs"
        ]

        print("数据库表数据检查:")
        print("=" * 50)

        for table in tables:
            try:
                result = await db.execute(
                    text(f"SELECT COUNT(*) as total FROM {table} WHERE is_deleted = 0")
                )
                total = result.scalar()
                print(f"{table}: {total} 条记录")
            except Exception as e:
                print(f"{table}: 查询失败 - {e}")

        # 检查 message_records 最近的数据
        print("\n" + "=" * 50)
        print("最近5条消息记录:")
        result = await db.execute(
            text("""
                SELECT id, msg_date, msg_type, inquirer, vin_code, source_group
                FROM message_records
                WHERE is_deleted = 0
                ORDER BY msg_date DESC
                LIMIT 5
            """)
        )
        records = result.fetchall()
        if records:
            for r in records:
                print(f"  {r.id}. [{r.msg_date}] {r.msg_type} - {r.inquirer} - {r.vin_code or '无VIN'}")
        else:
            print("  没有消息记录")


if __name__ == "__main__":
    asyncio.run(check_all_tables())
