import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional, List
from loguru import logger


class LogLevel(str, Enum):
    """日志级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class AsyncLogger:
    """异步日志管理器 - 支持INFO/WARNING/ERROR/LOGS分级存储"""

    def __init__(self):
        self.log_queue = asyncio.Queue()
        self.is_running = False
        self._setup_file_logger()

    def _setup_file_logger(self):
        """配置文件日志 - 按天为单位存储"""
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天零点切割
            retention="30 days",  # 保留30天
            level="INFO",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )

        # 按级别分文件存储
        logger.add(
            "logs/error_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            level="ERROR",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )

    async def start(self):
        """启动日志处理器"""
        self.is_running = True
        asyncio.create_task(self._log_processor())

    async def stop(self):
        """停止日志处理器"""
        self.is_running = False

    async def _log_processor(self):
        """日志处理循环 - 异步数据库日志提交"""
        while self.is_running:
            try:
                # 批量获取日志
                logs = []
                try:
                    while len(logs) < 10:
                        log = await asyncio.wait_for(self.log_queue.get(), timeout=0.1)
                        logs.append(log)
                except asyncio.TimeoutError:
                    pass

                # 批量写入数据库
                if logs:
                    await self._batch_save_to_db(logs)

            except Exception as e:
                logger.error(f"日志处理错误: {e}")

            await asyncio.sleep(0.1)

    async def log(
        self,
        level: LogLevel,
        message: str,
        user_id: Optional[int] = None,
        nickname: Optional[str] = None,
        ip_address: Optional[str] = None,
        login_location: Optional[str] = None,
        os: Optional[str] = None,
        browser: Optional[str] = None,
        operation: Optional[str] = None,
        operation_type: Optional[str] = None,
        extra: Optional[dict] = None
    ):
        """记录日志"""
        log_data = {
            "level": level.value,
            "message": message,
            "nickname": nickname,
            "ip_address": ip_address,
            "login_location": login_location,
            "os": os,
            "browser": browser,
            "login_time": datetime.utcnow(),
            "operation": operation,
            "operation_type": operation_type,
            "extra": extra or {}
        }

        # 写入文件日志
        if level == LogLevel.ERROR:
            logger.error(message)
        elif level == LogLevel.WARNING:
            logger.warning(message)
        else:
            logger.info(message)

        # 加入队列，异步写入数据库
        await self.log_queue.put(log_data)

    async def _batch_save_to_db(self, logs: List[dict]):
        """批量保存日志到数据库"""
        # TODO: 实现数据库写入逻辑
        pass

    # 便捷方法
    async def info(self, message: str, **kwargs):
        """INFO级别日志"""
        await self.log(LogLevel.INFO, message, **kwargs)

    async def warning(self, message: str, **kwargs):
        """WARNING级别日志"""
        await self.log(LogLevel.WARNING, message, **kwargs)

    async def error(self, message: str, **kwargs):
        """ERROR级别日志"""
        await self.log(LogLevel.ERROR, message, **kwargs)


# 全局日志实例
async_logger = AsyncLogger()
