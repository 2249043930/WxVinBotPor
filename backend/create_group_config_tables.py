#!/usr/bin/env python3
"""
创建群聊配置相关表
"""

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
            # 创建group_configs表
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS group_configs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    group_id VARCHAR(200) NOT NULL UNIQUE,
                    group_name VARCHAR(200),
                    customer_service_wxid VARCHAR(100),
                    customer_service_name VARCHAR(100),
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_group_id (group_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='群聊配置表 - 存储群客服和车型供应商绑定'
            """)
            print("[OK] group_configs表创建成功")
            
            # 创建group_model_suppliers表
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS group_model_suppliers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    group_config_id INT NOT NULL,
                    car_model_id INT NOT NULL,
                    supplier_id INT NOT NULL,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_config_id) REFERENCES group_configs(id) ON DELETE CASCADE,
                    FOREIGN KEY (car_model_id) REFERENCES car_models(id) ON DELETE CASCADE,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_group_model (group_config_id, car_model_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                COMMENT='群聊车型供应商绑定表'
            """)
            print("[OK] group_model_suppliers表创建成功")
            
            await conn.commit()
            print("\n所有表创建完成！")
            
    except Exception as e:
        print(f"[ERR] 创建表失败: {e}")
        await conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
