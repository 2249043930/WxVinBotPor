"""
修复 message_records 表的 image_content 字段类型为 LONGTEXT
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def fix_image_column():
    """修改 image_content 字段类型为 LONGTEXT"""
    # 创建同步引擎用于执行 ALTER TABLE
    from sqlalchemy import create_engine, text
    
    # 将 aiomysql 连接字符串转换为 pymysql
    sync_url = settings.DATABASE_URL.replace('mysql+aiomysql', 'mysql+pymysql')
    engine = create_engine(sync_url)
    
    with engine.connect() as conn:
        # 检查当前字段类型
        result = conn.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'message_records' AND COLUMN_NAME = 'image_content'
        """))
        row = result.fetchone()
        print(f"当前字段类型: {row}")
        
        # 修改字段类型为 LONGTEXT
        conn.execute(text("""
            ALTER TABLE message_records
            MODIFY COLUMN image_content LONGTEXT NULL COMMENT '图片内容（URL或Base64）'
        """))
        conn.commit()
        print("字段类型已修改为 LONGTEXT")
        
        # 验证修改结果
        result = conn.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'message_records' AND COLUMN_NAME = 'image_content'
        """))
        row = result.fetchone()
        print(f"修改后字段类型: {row}")
    
    engine.dispose()
    print("修复完成！")

if __name__ == "__main__":
    asyncio.run(fix_image_column())
