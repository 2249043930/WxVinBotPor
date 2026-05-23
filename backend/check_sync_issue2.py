"""
进一步检查智能同步问题
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_data():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 1. 检查源群的车型-供应商绑定 ===')
        result = await db.execute(text("""
            SELECT gms.id, gms.car_model_id, gms.supplier_id, g.group_name
            FROM group_model_suppliers gms
            JOIN group_configs g ON gms.group_config_id = g.id
            WHERE g.group_id = '47710019281@chatroom'
        """))
        bindings = result.fetchall()
        print(f'源群绑定数量: {len(bindings)}')
        for b in bindings[:5]:
            print(f'  - binding_id={b.id}, car_model_id={b.car_model_id}, supplier_id={b.supplier_id}')
        
        print('\n=== 2. 检查供应商表wxid字段 ===')
        result = await db.execute(text("""
            SELECT s.id, s.name, s.wxid
            FROM suppliers s
            LIMIT 10
        """))
        suppliers = result.fetchall()
        for s in suppliers:
            wxid_status = '有值' if s.wxid else '为空'
            print(f'  - {s.name} (id={s.id}): wxid={s.wxid} ({wxid_status})')
        
        print('\n=== 3. 检查car_model_supplier关联表 ===')
        result = await db.execute(text("""
            SELECT cms.car_model_id, cms.supplier_id
            FROM car_model_supplier cms
            LIMIT 10
        """))
        cms = result.fetchall()
        print(f'car_model_supplier记录数: {len(cms)}')
        for c in cms[:5]:
            print(f'  - car_model_id={c.car_model_id}, supplier_id={c.supplier_id}')
        
        print('\n=== 4. 检查源群配置详情 ===')
        result = await db.execute(text("""
            SELECT gc.id, gc.group_id, gc.group_name
            FROM group_configs gc
            WHERE gc.group_id = '47710019281@chatroom'
        """))
        config = result.fetchone()
        if config:
            print(f'  - config_id={config.id}, group_id={config.group_id}, name={config.group_name}')
        else:
            print('  - 未找到源群配置')

if __name__ == '__main__':
    asyncio.run(check_data())
