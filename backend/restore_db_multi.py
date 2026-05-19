"""
恢复数据库脚本 - 执行多条 SQL 语句
"""
import pymysql
import re

# 连接信息
host = 'localhost'
port = 3306
user = 'root'
password = '123456'
db_name = 'WxVinBot_vehicle_management'

# 先删除并创建数据库
conn = pymysql.connect(host=host, port=port, user=user, password=password, charset='utf8mb4')
cursor = conn.cursor()

print(f"删除旧数据库 {db_name}...")
cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")

print(f"创建新数据库 {db_name}...")
cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

cursor.close()
conn.close()

# 重新连接到新数据库
conn = pymysql.connect(
    host=host, port=port, user=user, password=password, 
    database=db_name, charset='utf8mb4',
    autocommit=False
)
cursor = conn.cursor()

# 读取 SQL 文件
print("读取SQL文件...")
with open('../WxVinBot_vehicle_management.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 禁用外键检查
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

# 分割 SQL 语句
# 使用正则表达式分割，但保留字符串内的分号
statements = []
current_statement = []
in_string = False
string_char = None

for char in sql_content:
    if char in ('\'', '"', '`'):
        if not in_string:
            in_string = True
            string_char = char
        elif char == string_char:
            # 检查是否是转义
            if current_statement and current_statement[-1] != '\\':
                in_string = False
                string_char = None
    
    current_statement.append(char)
    
    if char == ';' and not in_string:
        stmt = ''.join(current_statement).strip()
        if stmt:
            statements.append(stmt)
        current_statement = []

# 添加最后一条语句（如果没有分号结尾）
if current_statement:
    stmt = ''.join(current_statement).strip()
    if stmt:
        statements.append(stmt)

print(f"共 {len(statements)} 条 SQL 语句")

# 执行每条语句
success_count = 0
error_count = 0

for i, statement in enumerate(statements):
    # 跳过注释和空语句
    stmt_clean = statement.strip()
    if not stmt_clean or stmt_clean.startswith('--') or stmt_clean.startswith('/*') or stmt_clean.startswith('*'):
        continue
    
    try:
        cursor.execute(statement)
        success_count += 1
        if (i + 1) % 100 == 0:
            print(f"已执行 {i + 1}/{len(statements)} 条语句...")
    except Exception as e:
        error_count += 1
        # 只打印非忽略错误
        error_msg = str(e)
        if 'Duplicate' not in error_msg and 'FOREIGN KEY' not in error_msg:
            print(f"执行错误 ({i+1}): {error_msg[:100]}")

# 启用外键检查
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# 提交事务
conn.commit()

cursor.close()
conn.close()

print(f"\n数据库恢复完成！")
print(f"成功: {success_count} 条语句")
print(f"错误: {error_count} 条语句")
