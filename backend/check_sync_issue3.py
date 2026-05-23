"""
检查group_model_suppliers表数据
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_data():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 1. 检查group_model_suppliers表总记录数 ===')
        result = await db.execute(text('SELECT COUNT(*) as cnt FROM group_model_suppliers'))
        count = result.scalar()
        print(f'总记录数: {count}')
        
        print('\n=== 2. 检查源群的group_config_id ===')
        result = await db.execute(text("""
            SELECT id FROM group_configs WHERE group_id = '47710019281@chatroom'
        """))
        config = result.fetchone()
        if config:
            print(f'源群config_id: {config.id}')
            
            print('\n=== 3. 检查该config_id的绑定数量 ===')
            result = await db.execute(text("""
                SELECT COUNT(*) as cnt FROM group_model_suppliers 
                WHERE group_config_id = :config_id
            """), {'config_id': config.id})
            count = result.scalar()
            print(f'该config的绑定数: {count}')
            
            print('\n=== 4. 检查所有group_model_suppliers记录 ===')
            result = await db.execute(text("""
                SELECT gms.id, gms.group_config_id, gms.car_model_id, gms.supplier_id,
                       gc.group_id, gc.group_name
                FROM group_model_suppliers gms
                JOIN group_configs gc ON gms.group_config_id = gc.id
                LIMIT 20
            """))
            records = result.fetchall()
            for r in records:
                print(f'  - gms.id={r.id}, config_id={r.group_config_id}, car_model={r.car_model_id}, supplier={r.supplier_id}')
                print(f'    group={r.group_name} ({r.group_id})')
        
        print('\n=== 5. 检查是否有其他群的绑定 ===')
        result = await db.execute(text("""
            SELECT gc.group_id, gc.group_name, COUNT(*) as cnt
            FROM group_model_suppliers gms
            JOIN group_configs gc ON gms.group_config_id = gc.id
            WHERE gc.group_id != '47710019281@chatroom'
            GROUP BY gc.group_id
        """))
        other_groups = result.fetchall()
        print(f'其他群绑定数量: {len(other_groups)}')
        for g in other_groups:
            print(f'  - {g.group_name}: {g.cnt}个绑定')

if __name__ == '__main__':
    asyncio.run(check_data())
