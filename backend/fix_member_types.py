"""
修复 member_types 表数据
"""
import asyncio
import aiomysql

async def fix_member_types():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        db='WxVinBot_vehicle_management',
        charset='utf8mb4'
    )
    
    async with conn.cursor() as cur:
        # 检查 id=1 是否存在
        await cur.execute("SELECT * FROM member_types WHERE id = 1")
        row = await cur.fetchone()
        
        if not row:
            print("id=1 的记录不存在，正在插入...")
            await cur.execute("""
                INSERT INTO member_types (name, description, id, created_at, updated_at, is_deleted)
                VALUES ('金牌供应商', '合作3年以上，信誉良好', 1, '2026-05-08 14:43:14', '2026-05-08 14:43:14', 0)
            """)
            await conn.commit()
            print("插入成功！")
        else:
            print(f"id=1 的记录已存在: {row}")
        
        # 再次检查
        await cur.execute("SELECT * FROM member_types ORDER BY id")
        rows = await cur.fetchall()
        print(f"\n当前 member_types 表记录数: {len(rows)}")
        for row in rows:
            print(row)
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(fix_member_types())
