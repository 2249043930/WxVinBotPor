#!/usr/bin/env python3
"""测试车型API"""

import asyncio
import aiomysql

async def main():
    host = 'localhost'
    port = 3306
    user = 'root'
    password = '123456'
    database = 'WxVinBot_vehicle_management'
    
    conn = await aiomysql.connect(
        host=host, port=port, user=user, password=password,
        db=database, charset='utf8mb4'
    )
    
    try:
        async with conn.cursor() as cur:
            # 检查car_models表
            await cur.execute("SELECT COUNT(*) FROM car_models WHERE is_deleted = FALSE")
            count = await cur.fetchone()
            print(f"car_models表记录数: {count[0]}")
            
            # 查看所有车型
            await cur.execute("""
                SELECT id, name, brand, series 
                FROM car_models 
                WHERE is_deleted = FALSE
                ORDER BY brand, id
            """)
            records = await cur.fetchall()
            print(f"\n所有车型数据 ({len(records)}条):")
            for r in records:
                print(f"  ID={r[0]}, 名称={r[1]}, 品牌={r[2]}, 系列={r[3]}")
                
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
