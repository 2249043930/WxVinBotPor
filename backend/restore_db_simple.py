"""
简单恢复数据库脚本
使用 pymysql 执行 SQL 文件
"""
import pymysql

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
conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db_name, charset='utf8mb4')
cursor = conn.cursor()

# 读取并执行 SQL 文件
print("读取SQL文件...")
with open('../WxVinBot_vehicle_management.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# 执行整个 SQL 文件
print("执行SQL文件...")
try:
    cursor.execute(sql_content)
    conn.commit()
    print("SQL文件执行成功！")
except Exception as e:
    print(f"执行错误: {e}")
    conn.rollback()

cursor.close()
conn.close()
print("数据库恢复完成！")
