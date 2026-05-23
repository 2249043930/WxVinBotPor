"""
检查智能同步问题
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def check_data():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 1. 源群供应商wxid检查 ===')
        result = await db.execute(text("""
            SELECT DISTINCT s.wxid, s.name
            FROM suppliers s
            JOIN car_model_supplier cms ON s.id = cms.supplier_id
            JOIN group_model_suppliers gms ON cms.car_model_id = gms.car_model_id
            JOIN group_configs g ON gms.group_config_id = g.id
            WHERE g.group_id = '47710019281@chatroom'
              AND s.wxid IS NOT NULL
        """))
        suppliers = result.fetchall()
        print(f'源群供应商数量: {len(suppliers)}')
        for s in suppliers[:10]:
            print(f'  - {s.name}: {s.wxid}')
        
        print('\n=== 2. 群成员表数据检查 ===')
        result = await db.execute(text('SELECT COUNT(*) as cnt FROM group_members'))
        count = result.scalar()
        print(f'group_members表总记录数: {count}')
        
        result = await db.execute(text("""
            SELECT COUNT(*) as cnt 
            FROM group_members 
            WHERE group_id = '47710019281@chatroom'
        """))
        count = result.scalar()
        print(f'源群成员数: {count}')
        
        result = await db.execute(text("""
            SELECT group_id, COUNT(*) as cnt 
            FROM group_members 
            WHERE group_id != '47710019281@chatroom'
            GROUP BY group_id
            LIMIT 5
        """))
        groups = result.fetchall()
        print(f'\n其他群成员数(前5个):')
        for g in groups:
            print(f'  - {g.group_id}: {g.cnt}人')
        
        print('\n=== 3. wxid匹配检查 ===')
        total_matches = 0
        for sw in suppliers[:20]:  # 检查前20个供应商
            result = await db.execute(text("""
                SELECT COUNT(*) as cnt 
                FROM group_members 
                WHERE wxid = :wxid AND group_id != '47710019281@chatroom'
            """), {'wxid': sw.wxid})
            match_count = result.scalar()
            if match_count > 0:
                print(f'  供应商 {sw.name} ({sw.wxid}): 在其他群中出现 {match_count} 次')
                total_matches += match_count
        
        print(f'\n总匹配次数: {total_matches}')
        
        print('\n=== 4. 检查group_members表结构 ===')
        result = await db.execute(text('DESCRIBE group_members'))
        columns = result.fetchall()
        for col in columns:
            print(f'  - {col[0]}: {col[1]}')

if __name__ == '__main__':
    asyncio.run(check_data())
