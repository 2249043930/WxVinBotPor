"""
恢复数据库脚本
使用原始SQL文件恢复数据库结构和数据
"""
import asyncio
import aiomysql
from app.config import settings


async def restore_database():
    """从SQL文件恢复数据库"""
    # 解析数据库连接信息
    db_url = settings.DATABASE_URL
    # 提取数据库名
    db_name = db_url.split('/')[-1].split('?')[0]
    # 提取主机和端口
    host_port = db_url.split('@')[1].split('/')[0]
    if ':' in host_port:
        host, port = host_port.split(':')
        port = int(port)
    else:
        host = host_port
        port = 3306
    # 提取用户名和密码
    user_pass = db_url.split('://')[1].split('@')[0]
    if ':' in user_pass:
        user, password = user_pass.split(':')
    else:
        user = user_pass
        password = ''
    
    print(f"连接到数据库: {host}:{port}")
    print(f"数据库名: {db_name}")
    print(f"用户名: {user}")
    
    # 连接到MySQL（不指定数据库）
    conn = await aiomysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset='utf8mb4'
    )
    
    async with conn.cursor() as cur:
        # 删除旧数据库
        print(f"删除旧数据库 {db_name}...")
        await cur.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
        
        # 创建新数据库
        print(f"创建新数据库 {db_name}...")
        await cur.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # 使用数据库
        await cur.execute(f"USE `{db_name}`")
        
        # 读取SQL文件
        print("读取SQL文件...")
        import os
        sql_path = os.path.join('..', 'WxVinBot_vehicle_management.sql')
        if not os.path.exists(sql_path):
            sql_path = 'WxVinBot_vehicle_management.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句并执行
        print("执行SQL语句...")
        # 移除注释
        lines = sql_content.split('\n')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('/*') and not line.startswith('*'):
                filtered_lines.append(line)
        
        # 按分号分割语句
        statements = '\n'.join(filtered_lines).split(';')
        
        success_count = 0
        error_count = 0
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    await cur.execute(statement)
                    success_count += 1
                except Exception as e:
                    # 忽略某些错误（如外键约束等）
                    if 'FOREIGN KEY' in str(e) or 'Duplicate' in str(e):
                        pass
                    else:
                        error_count += 1
                        print(f"执行错误: {e}")
                        print(f"SQL: {statement[:100]}...")
        
        await conn.commit()
        
        print(f"\n恢复完成!")
        print(f"成功: {success_count} 条语句")
        print(f"错误: {error_count} 条语句")
    
    conn.close()
    print("数据库恢复成功！")


if __name__ == "__main__":
    asyncio.run(restore_database())
