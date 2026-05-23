"""
检查group_config_id
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_data():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 检查 group_configs 表 ===')
        result = await db.execute(text("""
            SELECT id, group_id, group_name
            FROM group_configs
            WHERE group_id IN ('47710019281@chatroom', '48152597680@chatroom')
        """))
        configs = result.fetchall()
        for c in configs:
            print(f'  - id={c.id}, group_id={c.group_id}, name={c.group_name}')
        
        print('\n=== 检查 group_model_suppliers 表中 group_config_id=11 的记录 ===')
        result = await db.execute(text("""
            SELECT gms.id, gms.group_config_id, gms.car_model_id, gms.supplier_id,
                   gc.group_id, gc.group_name
            FROM group_model_suppliers gms
            JOIN group_configs gc ON gms.group_config_id = gc.id
            WHERE gms.group_config_id = 11
        """))
        records = result.fetchall()
        print(f'找到 {len(records)} 条记录:')
        for r in records:
            print(f'  - gms.id={r.id}, config_id={r.group_config_id}, car_model={r.car_model_id}, supplier={r.supplier_id}')
            print(f'    group={r.group_name} ({r.group_id})')

if __name__ == '__main__':
    asyncio.run(check_data())
