"""
检查数据库中的 VIN 记录
"""
import asyncio
from app.db.session import async_session
from sqlalchemy import text

async def check_vin_records():
    """检查 VIN 记录表中的数据"""
    try:
        async with async_session() as db:
            # 查询 statistics 表中的数据
            result = await db.execute(text("""
                SELECT id, date, recognize_status, vin_code, car_model, 
                       source_group, inquirer, quoter, is_quoted, quote_time, supplier
                FROM statistics
                WHERE is_deleted = false
                ORDER BY date DESC
                LIMIT 10
            """))
            
            rows = result.fetchall()
            
            print("=" * 80)
            print(f"数据库中的 VIN 记录 (共 {len(rows)} 条)")
            print("=" * 80)
            
            if not rows:
                print("没有找到 VIN 记录！")
                print("\n可能的原因：")
                print("1. 还没有识别到任何 VIN 码")
                print("2. 数据保存在其他表中")
                print("3. 数据被标记为已删除")
            else:
                for row in rows:
                    print(f"\nID: {row.id}")
                    print(f"日期: {row.date}")
                    print(f"识别状态: {row.recognize_status}")
                    print(f"VIN: {row.vin_code}")
                    print(f"车型: {row.car_model}")
                    print(f"来源群: {row.source_group}")
                    print(f"询价人: {row.inquirer}")
                    print(f"报价人: {row.quoter}")
                    print(f"是否报价: {row.is_quoted}")
                    print("-" * 80)
            
            # 查询总数
            count_result = await db.execute(text("""
                SELECT COUNT(*) as total FROM statistics WHERE is_deleted = false
            """))
            total = count_result.scalar()
            print(f"\n总计: {total} 条记录")
            
    except Exception as e:
        print(f"查询失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_vin_records())
