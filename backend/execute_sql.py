#!/usr/bin/env python3
"""
执行SQL脚本添加表注释
"""

import asyncio
import aiomysql

async def main():
    # 数据库连接配置
    host = 'localhost'
    port = 3306
    user = 'root'
    password = '123456'
    database = 'WxVinBot_vehicle_management'
    
    # 表注释
    table_comments = {
        'users': '用户表 - 存储系统用户信息',
        'logs': '日志表 - 存储操作日志',
        'operation_logs': '操作日志表 - 存储详细操作记录',
        'accounts': '账号表 - 存储微信账号信息',
        'statistics': '统计表 - 存储VIN查询统计',
        'message_records': '消息记录表 - 存储群聊消息',
        'member_types': '成员类型表 - 存储供应商成员类型',
        'suppliers': '供应商表 - 存储供应商信息',
        'car_models': '车型表 - 存储车型配置信息',
        'car_model_supplier': '车型供应商关联表 - 车型与供应商多对多关系',
        'wechat_groups': '微信群表 - 存储群聊信息',
        'system_configs': '系统配置表 - 存储系统配置项',
        'api_configs': '接口配置表 - 存储API接口配置',
        'vin_info': 'VIN信息表 - 存储车架号查询结果',
    }
    
    # 连接数据库
    conn = await aiomysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=database,
        charset='utf8mb4'
    )
    
    try:
        async with conn.cursor() as cur:
            for table_name, comment in table_comments.items():
                sql = f"ALTER TABLE `{table_name}` COMMENT = %s"
                try:
                    await cur.execute(sql, (comment,))
                    print(f"[OK] 表 {table_name} 添加注释: {comment}")
                except Exception as e:
                    print(f"[ERR] 表 {table_name} 添加注释失败: {e}")
            
            await conn.commit()
            print("\n所有表注释添加完成！")
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
