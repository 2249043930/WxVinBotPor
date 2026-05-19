#!/usr/bin/env python3
"""
测试数据初始化脚本
为 WxVinBot Por 系统创建测试数据
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select

sys.path.insert(0, '.')

from app.db.session import async_session, engine
from app.models.base import Base
from app.models.user import User
from app.models.group import WechatGroup
from app.models.account import Account
from app.models.car_model import MemberType, Supplier, CarModel, car_model_supplier
from app.models.log import Log, OperationLog
from app.models.message import MessageRecord
from app.models.statistics import Statistics
from app.core.security import get_password_hash


async def init_database():
    """初始化数据库表"""
    async with engine.begin() as conn:
        # 删除所有表并重新创建
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] 数据库表已创建")


async def seed_users(db):
    """创建测试用户"""
    users_data = [
        {
            "nickname": "管理员",
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "phone": "13800138000",
            "email": "admin@wxvinbot.com",
            "is_active": True,
            "is_superuser": True,
            "wx_id": "wxid_admin_001",
            "wx_group_name": "汽配交流群",
            "group_member_wxid": "wxid_member_001"
        },
        {
            "nickname": "测试用户",
            "username": "user",
            "password_hash": get_password_hash("user123"),
            "phone": "13800138001",
            "email": "user@wxvinbot.com",
            "is_active": True,
            "is_superuser": False,
            "wx_id": "wxid_user_001",
            "wx_group_name": "汽配询价群",
            "group_member_wxid": "wxid_member_002"
        },
        {
            "nickname": "张三",
            "username": "zhangsan",
            "password_hash": get_password_hash("zs123456"),
            "phone": "13800138002",
            "email": "zhangsan@example.com",
            "is_active": True,
            "is_superuser": False,
            "wx_id": "wxid_zhangsan_001",
            "wx_group_name": "宝马配件群",
            "group_member_wxid": "wxid_member_003"
        },
        {
            "nickname": "李四",
            "username": "lisi",
            "password_hash": get_password_hash("ls123456"),
            "phone": "13800138003",
            "email": "lisi@example.com",
            "is_active": True,
            "is_superuser": False,
            "wx_id": "wxid_lisi_001",
            "wx_group_name": "奔驰配件群",
            "group_member_wxid": "wxid_member_004"
        },
        {
            "nickname": "王五",
            "username": "wangwu",
            "password_hash": get_password_hash("ww123456"),
            "phone": "13800138004",
            "email": "wangwu@example.com",
            "is_active": False,  # 禁用状态
            "is_superuser": False,
            "wx_id": "wxid_wangwu_001",
            "wx_group_name": "奥迪配件群",
            "group_member_wxid": "wxid_member_005"
        }
    ]

    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    
    await db.commit()
    print(f"[OK] 已创建 {len(users_data)} 个测试用户")
    return users_data


async def seed_accounts(db):
    """创建账户统计数据"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    accounts_data = [
        {"user_id": users[0].id, "llm_success_count": 150, "llm_fail_count": 10, "llm_success_rate": 93.75},
        {"user_id": users[1].id, "llm_success_count": 89, "llm_fail_count": 15, "llm_success_rate": 85.58},
        {"user_id": users[2].id, "llm_success_count": 245, "llm_fail_count": 20, "llm_success_rate": 92.45},
        {"user_id": users[3].id, "llm_success_count": 67, "llm_fail_count": 8, "llm_success_rate": 89.33},
    ]
    
    for account_data in accounts_data:
        account = Account(**account_data)
        db.add(account)
    
    await db.commit()
    print(f"[OK] 已创建 {len(accounts_data)} 个账户统计")


async def seed_wechat_groups(db):
    """创建微信群数据"""
    groups_data = [
        {
            "group_name": "宝马配件交流群",
            "group_id": "wx_group_bmw_001",
            "member_count": 128,
            "is_active": True,
            "inquiry_notify": True,
            "quote_notify": True,
            "delivery_notify": True,
            "deal_notify": True,
            "work_start_time": datetime.strptime("09:00", "%H:%M").time(),
            "work_end_time": datetime.strptime("18:00", "%H:%M").time(),
            "notify_keywords": "询价,报价,配件,车架号"
        },
        {
            "group_name": "奔驰配件供应群",
            "group_id": "wx_group_benz_001",
            "member_count": 256,
            "is_active": True,
            "inquiry_notify": True,
            "quote_notify": True,
            "delivery_notify": False,
            "deal_notify": True,
            "work_start_time": datetime.strptime("08:30", "%H:%M").time(),
            "work_end_time": datetime.strptime("17:30", "%H:%M").time(),
            "notify_keywords": "奔驰,配件,原厂"
        },
        {
            "group_name": "奥迪配件询价群",
            "group_id": "wx_group_audi_001",
            "member_count": 89,
            "is_active": True,
            "inquiry_notify": True,
            "quote_notify": False,
            "delivery_notify": True,
            "deal_notify": False,
            "work_start_time": datetime.strptime("09:00", "%H:%M").time(),
            "work_end_time": datetime.strptime("18:00", "%H:%M").time(),
            "notify_keywords": "奥迪,A4,A6,Q5"
        },
        {
            "group_name": "大众配件批发群",
            "group_id": "wx_group_vw_001",
            "member_count": 312,
            "is_active": True,
            "inquiry_notify": True,
            "quote_notify": True,
            "delivery_notify": True,
            "deal_notify": True,
            "work_start_time": datetime.strptime("08:00", "%H:%M").time(),
            "work_end_time": datetime.strptime("19:00", "%H:%M").time(),
            "notify_keywords": "大众,帕萨特,迈腾,速腾"
        },
        {
            "group_name": "日系车配件群",
            "group_id": "wx_group_jp_001",
            "member_count": 167,
            "is_active": False,  # 禁用
            "inquiry_notify": True,
            "quote_notify": True,
            "delivery_notify": True,
            "deal_notify": True,
            "work_start_time": datetime.strptime("09:00", "%H:%M").time(),
            "work_end_time": datetime.strptime("18:00", "%H:%M").time(),
            "notify_keywords": "丰田,本田,日产"
        }
    ]
    
    for group_data in groups_data:
        group = WechatGroup(**group_data)
        db.add(group)
    
    await db.commit()
    print(f"[OK] 已创建 {len(groups_data)} 个微信群")


async def seed_member_types(db):
    """创建成员类型"""
    types_data = [
        {"name": "金牌供应商", "description": "合作3年以上，信誉良好"},
        {"name": "银牌供应商", "description": "合作1-3年，信誉良好"},
        {"name": "普通供应商", "description": "新合作供应商"},
        {"name": "VIP客户", "description": "大客户，优先处理"},
        {"name": "普通客户", "description": "一般客户"}
    ]
    
    for type_data in types_data:
        member_type = MemberType(**type_data)
        db.add(member_type)
    
    await db.commit()
    print(f"[OK] 已创建 {len(types_data)} 个成员类型")


async def seed_suppliers(db):
    """创建汽配商数据"""
    suppliers_data = [
        {"wxid": "wxid_supplier_001", "name": "北京宝马配件中心", "member_type_id": 1},
        {"wxid": "wxid_supplier_002", "name": "上海奔驰汽配", "member_type_id": 1},
        {"wxid": "wxid_supplier_003", "name": "广州奥迪配件", "member_type_id": 2},
        {"wxid": "wxid_supplier_004", "name": "深圳大众配件", "member_type_id": 2},
        {"wxid": "wxid_supplier_005", "name": "成都丰田汽配", "member_type_id": 3},
        {"wxid": "wxid_supplier_006", "name": "武汉本田配件", "member_type_id": 3},
        {"wxid": "wxid_supplier_007", "name": "杭州日产汽配", "member_type_id": 4},
        {"wxid": "wxid_supplier_008", "name": "南京福特配件", "member_type_id": 5}
    ]
    
    for supplier_data in suppliers_data:
        supplier = Supplier(**supplier_data)
        db.add(supplier)
    
    await db.commit()
    print(f"[OK] 已创建 {len(suppliers_data)} 个汽配商")


async def seed_car_models(db):
    """创建车型数据"""
    car_models_data = [
        {"name": "宝马 3系 320Li", "brand": "宝马", "series": "3系", "displacement": "2.0T", "year": "2020"},
        {"name": "宝马 5系 530Li", "brand": "宝马", "series": "5系", "displacement": "2.0T", "year": "2021"},
        {"name": "宝马 X3 xDrive28i", "brand": "宝马", "series": "X3", "displacement": "2.0T", "year": "2022"},
        {"name": "奔驰 C级 C260L", "brand": "奔驰", "series": "C级", "displacement": "1.5T", "year": "2021"},
        {"name": "奔驰 E级 E300L", "brand": "奔驰", "series": "E级", "displacement": "2.0T", "year": "2022"},
        {"name": "奔驰 GLC GLC260", "brand": "奔驰", "series": "GLC", "displacement": "2.0T", "year": "2021"},
        {"name": "奥迪 A4L 40TFSI", "brand": "奥迪", "series": "A4L", "displacement": "2.0T", "year": "2022"},
        {"name": "奥迪 A6L 45TFSI", "brand": "奥迪", "series": "A6L", "displacement": "2.0T", "year": "2021"},
        {"name": "奥迪 Q5L 40TFSI", "brand": "奥迪", "series": "Q5L", "displacement": "2.0T", "year": "2022"},
        {"name": "大众 帕萨特 330TSI", "brand": "大众", "series": "帕萨特", "displacement": "2.0T", "year": "2021"},
        {"name": "大众 迈腾 380TSI", "brand": "大众", "series": "迈腾", "displacement": "2.0T", "year": "2022"},
        {"name": "大众 速腾 280TSI", "brand": "大众", "series": "速腾", "displacement": "1.4T", "year": "2021"}
    ]
    
    for car_model_data in car_models_data:
        car_model = CarModel(**car_model_data)
        db.add(car_model)
    
    await db.commit()
    print(f"[OK] 已创建 {len(car_models_data)} 个车型")


async def seed_car_model_suppliers(db):
    """创建车型和汽配商的关联"""
    from sqlalchemy import insert
    
    # 获取刚创建的记录ID
    result = await db.execute(select(CarModel.id))
    car_model_ids = [r[0] for r in result.all()]
    
    result = await db.execute(select(Supplier.id))
    supplier_ids = [r[0] for r in result.all()]
    
    # 建立关联关系 - 使用直接插入关联表
    associations = [
        # 宝马车型 -> 宝马配件中心
        {"supplier_id": supplier_ids[0], "car_model_id": car_model_ids[0]},  # 3系
        {"supplier_id": supplier_ids[0], "car_model_id": car_model_ids[1]},  # 5系
        {"supplier_id": supplier_ids[0], "car_model_id": car_model_ids[2]},  # X3
        # 奔驰车型 -> 上海奔驰汽配
        {"supplier_id": supplier_ids[1], "car_model_id": car_model_ids[3]},  # C级
        {"supplier_id": supplier_ids[1], "car_model_id": car_model_ids[4]},  # E级
        {"supplier_id": supplier_ids[1], "car_model_id": car_model_ids[5]},  # GLC
        # 奥迪车型 -> 广州奥迪配件
        {"supplier_id": supplier_ids[2], "car_model_id": car_model_ids[6]},  # A4L
        {"supplier_id": supplier_ids[2], "car_model_id": car_model_ids[7]},  # A6L
        {"supplier_id": supplier_ids[2], "car_model_id": car_model_ids[8]},  # Q5L
        # 大众车型 -> 深圳大众配件
        {"supplier_id": supplier_ids[3], "car_model_id": car_model_ids[9]},   # 帕萨特
        {"supplier_id": supplier_ids[3], "car_model_id": car_model_ids[10]},  # 迈腾
        {"supplier_id": supplier_ids[3], "car_model_id": car_model_ids[11]},  # 速腾
    ]
    
    for assoc in associations:
        await db.execute(insert(car_model_supplier).values(**assoc))
    
    await db.commit()
    print("[OK] 已创建车型和汽配商的关联关系")


async def seed_logs(db):
    """创建登录日志"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    logs_data = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(50):
        user = users[i % len(users)]
        log = Log(
            user_id=user.id,
            nickname=user.nickname,
            ip_address=f"192.168.1.{i % 255}",
            login_location=f"北京市朝阳区",
            os="Windows 10" if i % 2 == 0 else "MacOS",
            browser="Chrome" if i % 3 == 0 else "Firefox" if i % 3 == 1 else "Edge",
            login_time=base_time + timedelta(hours=i*2)
        )
        logs_data.append(log)
    
    for log in logs_data:
        db.add(log)
    
    await db.commit()
    print(f"[OK] 已创建 {len(logs_data)} 条登录日志")


async def seed_operation_logs(db):
    """创建操作日志"""
    operations = [
        "登录系统", "修改用户信息", "添加微信群", "删除汽配商",
        "更新车型数据", "查看统计报表", "导出数据", "修改密码",
        "配置LLM", "查看消息记录"
    ]
    
    operation_types = ["查询", "新增", "修改", "删除", "导出"]
    
    logs_data = []
    base_time = datetime.now() - timedelta(days=15)
    
    for i in range(100):
        log = OperationLog(
            nickname=f"用户{i % 5 + 1}",
            ip_address=f"192.168.1.{i % 255}",
            login_location=f"上海市浦东新区" if i % 2 == 0 else "广州市天河区",
            os="Windows 11" if i % 2 == 0 else "MacOS",
            browser="Chrome",
            login_time=base_time + timedelta(hours=i),
            operation=operations[i % len(operations)],
            operation_type=operation_types[i % len(operation_types)]
        )
        logs_data.append(log)
    
    for log in logs_data:
        db.add(log)
    
    await db.commit()
    print(f"[OK] 已创建 {len(logs_data)} 条操作日志")


async def seed_message_records(db):
    """创建消息记录"""
    vins = [
        "LBV5S310XFSL12345",
        "LE4ZG4CB8JL123456",
        "LFV3A23C8J3123456",
        "LSVAG2180J2123456",
        "LGXC14AA8J8123456"
    ]
    
    car_models_list = [
        "宝马 3系 320Li 2020款",
        "奔驰 C级 C260L 2021款",
        "奥迪 A4L 40TFSI 2022款",
        "大众 帕萨特 330TSI 2021款",
        "丰田 凯美瑞 2.5G 2022款"
    ]
    
    groups = ["宝马配件交流群", "奔驰配件供应群", "奥迪配件询价群", "大众配件批发群"]
    inquirers = ["张三", "李四", "王五", "赵六", "钱七"]
    
    messages_data = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(200):
        msg_type = "text" if i % 3 == 0 else "image" if i % 3 == 1 else "voice"
        
        msg = MessageRecord(
            msg_type=msg_type,
            image_content=f"https://example.com/image_{i}.jpg" if msg_type == "image" else None,
            msg_date=base_time + timedelta(minutes=i*10),
            inquirer=inquirers[i % len(inquirers)],
            vin_code=vins[i % len(vins)],
            car_model=car_models_list[i % len(car_models_list)],
            source_group=groups[i % len(groups)],
            raw_message=f"询价：{vins[i % len(vins)]} 前保险杠" if i % 2 == 0 else f"车架号：{vins[i % len(vins)]}"
        )
        messages_data.append(msg)
    
    for msg in messages_data:
        db.add(msg)
    
    await db.commit()
    print(f"[OK] 已创建 {len(messages_data)} 条消息记录")


async def seed_statistics(db):
    """创建车架号识别统计记录"""
    vins = [
        "LBV5S310XFSL12345",
        "LE4ZG4CB8JL123456",
        "LFV3A23C8J3123456",
        "LSVAG2180J2123456",
        "LGXC14AA8J8123456",
        "WBAWL510X0PX12345",
        "WDDUG8CB9EA123456"
    ]

    car_models_list = [
        "宝马 3系 320Li 2020款",
        "奔驰 C级 C260L 2021款",
        "奥迪 A4L 40TFSI 2022款",
        "大众 帕萨特 330TSI 2021款",
        "丰田 凯美瑞 2.5G 2022款",
        "宝马 5系 530Li 2021款",
        "奔驰 E级 E300L 2020款"
    ]

    groups = ["宝马配件交流群", "奔驰配件供应群", "奥迪配件询价群", "大众配件批发群", "丰田汽配总群"]
    inquirers = ["张三", "李四", "王五", "赵六", "钱七"]
    quoters = ["刘供应商", "陈供应商", "杨供应商", "黄供应商", None, None]
    suppliers = ["北京宝马汽配", "上海奔驰配件", "广州奥迪专营", "深圳大众汽配", "东莞丰田配件"]

    statistics_data = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(150):
        is_success = i % 10 != 0  # 90%成功率
        is_quoted = is_success and (i % 3 == 0)  # 成功的记录中30%已报价

        record = Statistics(
            date=base_time + timedelta(hours=i * 2),
            recognize_status="success" if is_success else "fail",
            vin_code=vins[i % len(vins)] if is_success else None,
            car_model=car_models_list[i % len(car_models_list)] if is_success else None,
            source_group=groups[i % len(groups)],
            inquirer=inquirers[i % len(inquirers)],
            quoter=quoters[i % len(quoters)] if is_quoted else None,
            is_quoted=is_quoted,
            quote_time=(i % 60) + 10 if is_quoted else None,  # 10-70分钟
            supplier=suppliers[i % len(suppliers)] if is_quoted else None
        )
        statistics_data.append(record)

    for record in statistics_data:
        db.add(record)

    await db.commit()
    print(f"[OK] 已创建 {len(statistics_data)} 条车架号识别记录")


async def main():
    """主函数"""
    print("=" * 60)
    print("WxVinBot Por 测试数据初始化")
    print("=" * 60)
    
    # 初始化数据库
    await init_database()
    
    async with async_session() as db:
        # 创建测试数据
        await seed_users(db)
        await seed_accounts(db)
        await seed_wechat_groups(db)
        await seed_member_types(db)
        await seed_suppliers(db)
        await seed_car_models(db)
        await seed_car_model_suppliers(db)
        await seed_logs(db)
        await seed_operation_logs(db)
        await seed_message_records(db)
        await seed_statistics(db)
    
    print("=" * 60)
    print("[OK] 测试数据初始化完成！")
    print("=" * 60)
    print("\n登录账号信息：")
    print("  - 管理员: admin / admin123")
    print("  - 测试用户: user / user123")
    print("  - 张三: zhangsan / zs123456")
    print("  - 李四: lisi / ls123456")
    print("  - 王五(禁用): wangwu / ww123456")


if __name__ == "__main__":
    asyncio.run(main())
