"""
千寻框架 HTTP 回调接口
接收千寻框架推送的群聊消息
"""

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.db.session import get_db
from app.core.security import get_current_user
from app.modules.wxbot.message_parser import MessageParser
from app.modules.wxbot.message_handler import GroupMessageHandler
from app.modules.wxbot.bot import QianxunBot
from loguru import logger

router = APIRouter()

# 全局消息处理器
_message_handler: GroupMessageHandler = None


def get_message_handler() -> GroupMessageHandler:
    """获取全局消息处理器"""
    global _message_handler
    if _message_handler is None:
        bot = QianxunBot()
        _message_handler = GroupMessageHandler(bot)
    return _message_handler


@router.post("/wechat")
async def wechat_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    接收千寻框架推送的消息
    
    千寻框架配置：
    - WebSocket客户端 -> HTTP API服务端
    - 服务端地址: http://127.0.0.1:8000/api/v1/callback/wechat
    """
    try:
        # 获取原始消息数据
        data = await request.json()
        logger.info(f"收到千寻框架回调: {str(data)[:200]}...")
        
        # 解析消息 - 将JSON对象转换为字符串再解析
        import json
        parser = MessageParser()
        message_str = json.dumps(data) if isinstance(data, dict) else str(data)
        parsed_msg = parser.parse(message_str)
        
        if not parsed_msg:
            logger.debug("消息解析失败或不需要处理")
            return {"code": 0, "message": "success"}
        
        group_id = parsed_msg.get("from_wxid")
        sender_wxid = parsed_msg.get("sender_wxid")
        msg_type = parsed_msg.get("msg_type")
        
        logger.info(f"解析消息成功 - 群ID: {group_id}, 发送者: {sender_wxid}, 类型: {msg_type}")
        
        # 获取消息处理器并处理消息
        handler = get_message_handler()
        await handler.initialize()
        
        # 根据消息类型调用对应的处理器
        if msg_type == "text":
            await handler.handle_text_message(parsed_msg)
        elif msg_type == "image":
            await handler.handle_image_message(parsed_msg)
        elif msg_type == "voice":
            await handler.handle_voice_message(parsed_msg)
        elif msg_type == "video":
            await handler.handle_video_message(parsed_msg)
        else:
            logger.warning(f"未知的消息类型: {msg_type}")
        
        return {"code": 0, "message": "success"}
        
    except Exception as e:
        logger.error(f"处理回调消息失败: {e}")
        return {"code": 1, "message": f"error: {str(e)}"}


@router.get("/test")
async def test_callback():
    """测试回调接口是否正常工作"""
    return {"code": 0, "message": "回调接口正常工作"}
