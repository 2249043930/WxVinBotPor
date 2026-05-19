#!/usr/bin/env python3
"""
数据库初始化脚本
用于在新环境部署时创建所有数据库表
"""

import asyncio
import sys

sys.path.insert(0, '.')

from app.db.session import engine
from app.models.base import Base
from app.models import (
    User, Log, OperationLog, Account, Statistics, MessageRecord,
    MemberType, Supplier, CarModel, car_model_supplier,
    WechatGroup, GroupConfig, GroupModelSupplier, group_model_supplier,
    SystemConfig, ApiConfig, VinInfo, VinRecord
)
from loguru import logger


async def init_database():
    """初始化数据库 - 创建所有表"""
    try:
        logger.info("开始初始化数据库...")
        
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("✅ 数据库表创建成功！")
        
        # 列出所有创建的表
        from sqlalchemy import inspect
        
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        
        async with engine.connect() as conn:
            tables = await conn.run_sync(get_tables)
            logger.info(f"已创建的表 ({len(tables)} 个):")
            for table in sorted(tables):
                logger.info(f"  - {table}")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def reset_database():
    """重置数据库 - 删除所有表并重新创建"""
    try:
        logger.warning("⚠️  正在重置数据库，所有数据将被删除！")
        
        async with engine.begin() as conn:
            # 删除所有表
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("已删除所有表")
            
            # 重新创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("已重新创建所有表")
            
        logger.info("✅ 数据库重置成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化工具")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置数据库（删除所有数据并重新创建表）"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        # 重置数据库
        result = asyncio.run(reset_database())
    else:
        # 初始化数据库（仅创建不存在的表）
        result = asyncio.run(init_database())
    
    sys.exit(0 if result else 1)
