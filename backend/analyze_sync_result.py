"""
分析智能同步结果 - 检查跳过原因
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def analyze():
    engine = create_async_engine('mysql+aiomysql://root:123456@localhost:3306/WxVinBot_vehicle_management')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print('=== 1. 检查源群配置 ===')
        result = await db.execute(text("""
            SELECT gc.id, gc.group_id, gc.group_name
            FROM group_configs gc
            WHERE gc.group_id = '47710019281@chatroom'
        """))
        source_config = result.fetchone()
        if source_config:
            print(f"源群: id={source_config.id}, name={source_config.group_name}")
            
            # 获取源群绑定
            result = await db.execute(text("""
                SELECT gms.car_model_id, gms.supplier_id, cm.name as car_model_name, s.name as supplier_name, s.wxid
                FROM group_model_suppliers gms
                JOIN car_models cm ON gms.car_model_id = cm.id
                JOIN suppliers s ON gms.supplier_id = s.id
                WHERE gms.group_config_id = :config_id
            """), {"config_id": source_config.id})
            bindings = result.fetchall()
            print(f"\n源群绑定数量: {len(bindings)}")
            for b in bindings:
                print(f"  - 车型: {b.car_model_name} (id={b.car_model_id}), 供应商: {b.supplier_name} (id={b.supplier_id}, wxid={b.wxid})")
        
        print('\n=== 2. 检查目标群的绑定情况 ===')
        # 获取所有目标群
        result = await db.execute(text("""
            SELECT gc.id, gc.group_id, gc.group_name
            FROM group_configs gc
            WHERE gc.group_id != '47710019281@chatroom'
        """))
        target_configs = result.fetchall()
        
        total_groups = len(target_configs)
        has_binding_groups = 0
        no_binding_groups = 0
        
        for tc in target_configs:
            result = await db.execute(text("""
                SELECT COUNT(*) as count
                FROM group_model_suppliers
                WHERE group_config_id = :config_id
            """), {"config_id": tc.id})
            count = result.fetchone().count
            
            if count > 0:
                has_binding_groups += 1
            else:
                no_binding_groups += 1
        
        print(f"总目标群数: {total_groups}")
        print(f"已有绑定的群: {has_binding_groups}")
        print(f"无绑定的群: {no_binding_groups}")
        
        print('\n=== 3. 检查群成员情况 ===')
        result = await db.execute(text("""
            SELECT group_id, COUNT(*) as count
            FROM group_members
            GROUP BY group_id
        """))
        member_counts = result.fetchall()
        
        groups_with_members = len(member_counts)
        total_members = sum(m.count for m in member_counts)
        
        print(f"有成员的群数: {groups_with_members}")
        print(f"总成员数: {total_members}")
        
        # 检查供应商成员
        result = await db.execute(text("""
            SELECT DISTINCT gm.group_id
            FROM group_members gm
            WHERE gm.wxid = 'wxid_668hehsouqmo12'
        """))
        groups_with_supplier = [r.group_id for r in result.fetchall()]
        print(f"\n包含供应商 wxid_668hehsouqmo12 的群数: {len(groups_with_supplier)}")
        
        print('\n=== 4. 分析可能的同步结果 ===')
        # 源群供应商wxid
        supplier_wxid = 'wxid_668hehsouqmo12'
        car_model_id = 26
        
        # 统计
        would_create = 0
        would_skip_exists = 0
        would_skip_no_member = 0
        would_skip_same_model = 0
        
        for tc in target_configs:
            # 检查是否有此供应商成员
            result = await db.execute(text("""
                SELECT COUNT(*) as count
                FROM group_members
                WHERE group_id = :group_id AND wxid = :wxid
            """), {"group_id": tc.group_id, "wxid": supplier_wxid})
            has_member = result.fetchone().count > 0
            
            # 检查是否已有绑定
            result = await db.execute(text("""
                SELECT car_model_id, supplier_id
                FROM group_model_suppliers
                WHERE group_config_id = :config_id
            """), {"config_id": tc.id})
            existing = result.fetchall()
            
            has_same_binding = any(e.car_model_id == car_model_id and e.supplier_id == 10 for e in existing)
            has_same_model = any(e.car_model_id == car_model_id for e in existing)
            
            if has_same_binding:
                would_skip_exists += 1
            elif has_same_model:
                would_skip_same_model += 1
            elif not has_member:
                would_skip_no_member += 1
            else:
                would_create += 1
        
        print(f"预计创建绑定: {would_create}")
        print(f"预计跳过(已存在): {would_skip_exists}")
        print(f"预计跳过(同车型不同供应商): {would_skip_same_model}")
        print(f"预计跳过(无此供应商成员): {would_skip_no_member}")

if __name__ == '__main__':
    asyncio.run(analyze())
