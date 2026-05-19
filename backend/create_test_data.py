"""
创建测试数据到 statistics 表
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from sqlalchemy import text


async def create_test_data():
    """创建测试数据"""
    async with async_session() as db:
        # 插入测试数据
        test_data = [
            {
                "date": datetime.now(),
                "recognize_status": "success",
                "vin_code": "LSVAG2180E2100001",
                "car_model": "大众帕萨特 2014款 1.8TSI DSG御尊版",
                "source_group": "机器人测试群1",
                "inquirer": "大雄",  # 测试昵称显示
                "quoter": "汽配链供应商A",  # 测试供应商名称显示
                "is_quoted": True,
                "quote_time": 15,
                "supplier": "汽配链供应商A"
            },
            {
                "date": datetime.now(),
                "recognize_status": "success",
                "vin_code": "LVGBE40K28G000002",
                "car_model": "丰田凯美瑞 2008款 240G 豪华版",
                "source_group": "机器人测试群1",
                "inquirer": "Muke～",  # 测试昵称显示
                "quoter": "汽配链供应商B",
                "is_quoted": False,
                "quote_time": None,
                "supplier": None
            },
            {
                "date": datetime.now(),
                "recognize_status": "fail",
                "vin_code": None,
                "car_model": None,
                "source_group": "机器人测试群1",
                "inquirer": "测试用户",
                "quoter": None,
                "is_quoted": False,
                "quote_time": None,
                "supplier": None
            }
        ]

        for data in test_data:
            await db.execute(
                text("""
                    INSERT INTO statistics
                    (date, recognize_status, vin_code, car_model, source_group,
                     inquirer, quoter, is_quoted, quote_time, supplier,
                     created_at, updated_at, is_deleted)
                    VALUES
                    (:date, :recognize_status, :vin_code, :car_model, :source_group,
                     :inquirer, :quoter, :is_quoted, :quote_time, :supplier,
                     NOW(), NOW(), 0)
                """),
                data
            )

        await db.commit()
        print("测试数据创建成功！")

        # 查询验证
        result = await db.execute(
            text("SELECT COUNT(*) as total FROM statistics WHERE is_deleted = 0")
        )
        total = result.scalar()
        print(f"当前 statistics 表记录数: {total}")


if __name__ == "__main__":
    asyncio.run(create_test_data())
