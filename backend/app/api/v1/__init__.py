from fastapi import APIRouter
from app.api.v1 import auth, dashboard, user, api_config, log, car_model, group, vin, statistics, bot, wechat, account, callback, group_config

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["数据看板"])
api_router.include_router(user.router, prefix="/user", tags=["用户管理"])
api_router.include_router(api_config.router, prefix="/api-config", tags=["接口配置"])
api_router.include_router(log.router, prefix="/log", tags=["日志管理"])
api_router.include_router(car_model.router, prefix="/car-model", tags=["车型配置"])
api_router.include_router(group.router, prefix="/group", tags=["厂群管理"])
api_router.include_router(vin.router, prefix="/vin", tags=["车架号记录"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["数据统计"])
api_router.include_router(bot.router, prefix="/bot", tags=["微信机器人"])
api_router.include_router(wechat.router, prefix="/wechat", tags=["微信管理"])
api_router.include_router(account.router, prefix="/account", tags=["账户管理"])
api_router.include_router(callback.router, prefix="/callback", tags=["消息回调"])
api_router.include_router(group_config.router, prefix="/group-config", tags=["群聊配置"])

__all__ = ["api_router"]
