"""
检查数据库数据
"""
import asyncio
import aiomysql

async def check_db():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        db='WxVinBot_vehicle_management',
        charset='utf8mb4'
    )
    
    async with conn.cursor() as cur:
        # 检查 member_types 表
        print("=== member_types 表 ===")
        await cur.execute("SELECT * FROM member_types")
        rows = await cur.fetchall()
        print(f"记录数: {len(rows)}")
        for row in rows:
            print(row)
        
        # 检查 suppliers 表
        print("\n=== suppliers 表 ===")
        await cur.execute("SELECT * FROM suppliers LIMIT 5")
        rows = await cur.fetchall()
        print(f"记录数: {len(rows)}")
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(check_db())
