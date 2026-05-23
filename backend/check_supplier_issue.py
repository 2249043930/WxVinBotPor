"""
检查供应商ID问题
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_data():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 1. 检查源群的供应商绑定 ===')
        result = await db.execute(text("""
            SELECT gms.id, gms.car_model_id, gms.supplier_id, s.name, s.wxid
            FROM group_model_suppliers gms
            JOIN group_configs gc ON gms.group_config_id = gc.id
            JOIN suppliers s ON gms.supplier_id = s.id
            WHERE gc.group_id = '47710019281@chatroom'
        """))
        bindings = result.fetchall()
        print(f'源群绑定数量: {len(bindings)}')
        for b in bindings:
            print(f'  - gms.id={b.id}, car_model_id={b.car_model_id}, supplier_id={b.supplier_id}, name={b.name}, wxid={b.wxid}')
        
        print('\n=== 2. 检查目标群 48152597680@chatroom 的供应商绑定 ===')
        result = await db.execute(text("""
            SELECT gms.id, gms.car_model_id, gms.supplier_id, s.name, s.wxid
            FROM group_model_suppliers gms
            JOIN group_configs gc ON gms.group_config_id = gc.id
            JOIN suppliers s ON gms.supplier_id = s.id
            WHERE gc.group_id = '48152597680@chatroom'
        """))
        bindings = result.fetchall()
        print(f'目标群绑定数量: {len(bindings)}')
        for b in bindings:
            print(f'  - gms.id={b.id}, car_model_id={b.car_model_id}, supplier_id={b.supplier_id}, name={b.name}, wxid={b.wxid}')
        
        print('\n=== 3. 检查供应商表中 wxid_668hehsouqmo12 的记录 ===')
        result = await db.execute(text("""
            SELECT id, name, wxid
            FROM suppliers
            WHERE wxid = 'wxid_668hehsouqmo12'
        """))
        suppliers = result.fetchall()
        print(f'找到 {len(suppliers)} 个供应商记录:')
        for s in suppliers:
            print(f'  - id={s.id}, name={s.name}, wxid={s.wxid}')

if __name__ == '__main__':
    asyncio.run(check_data())
