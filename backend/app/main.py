from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.v1 import api_router
from app.core.middleware import setup_middleware
from app.core.logger import setup_logger
from app.db.session import engine
from app.models.base import Base
from loguru import logger


# 配置日志
setup_logger()

# 全局BotManager实例
bot_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # 创建数据库表（如果不存在）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables checked/created")

    # 启动微信机器人管理器
    global bot_manager
    try:
        from app.modules.wxbot.bot_manager import BotManager
        bot_manager = BotManager()
        # 使用asyncio.create_task在后台启动，不阻塞FastAPI启动
        import asyncio
        asyncio.create_task(bot_manager.start())
        logger.info("微信机器人管理器已启动")
    except Exception as e:
        logger.error(f"启动微信机器人管理器失败: {e}")

    yield

    # 关闭时执行
    logger.info(f"Shutting down {settings.APP_NAME}")
    if bot_manager:
        try:
            await bot_manager.stop()
            logger.info("微信机器人管理器已停止")
        except Exception as e:
            logger.error(f"停止微信机器人管理器失败: {e}")
    await engine.dispose()


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="WxVinBot Pro - 基于微信群的汽车配件询价管理系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置中间件
setup_middleware(app)

# 注册路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
