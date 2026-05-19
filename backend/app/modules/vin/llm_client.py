import re
import json
from typing import Dict, Any, Optional
import httpx
from loguru import logger
from app.config import settings
from app.db.session import async_session
from app.services.api_config_service import ApiConfigService


class LLMClient:
    """LLM多模态API客户端 - 支持Kimi/Moonshot
    
    支持两种方式调用:
    1. OpenAI SDK方式 (推荐) - 使用openai库
    2. HTTP API方式 - 使用httpx直接调用
    """

    def __init__(self):
        self._api_config = None
        self._openai_client = None

    async def _get_api_config(self):
        """从数据库获取LLM API配置"""
        try:
            async with async_session() as db:
                service = ApiConfigService(db)
                config = await service.get_default_by_type("llm")
                if config:
                    self._api_config = {
                        "api_key": config.api_key,
                        "api_base": config.api_base or "https://api.moonshot.cn/v1",
                        "model": config.model or "moonshot-v1-8k-vision-preview",
                        "temperature": float(config.temperature) if config.temperature else 0.1,
                        "max_tokens": config.max_tokens or 2000
                    }
                    logger.info(f"从数据库加载LLM配置: {config.name}")
                else:
                    # 使用环境变量配置
                    self._api_config = {
                        "api_key": settings.LLM_API_KEY,
                        "api_base": settings.LLM_API_BASE or "https://api.moonshot.cn/v1",
                        "model": settings.LLM_MODEL or "moonshot-v1-8k-vision-preview",
                        "temperature": settings.LLM_TEMPERATURE or 0.1,
                        "max_tokens": settings.LLM_MAX_TOKENS or 2000
                    }
                    logger.warning("数据库中没有LLM配置，使用环境变量配置")
        except Exception as e:
            logger.error(f"获取LLM配置失败: {e}")
            # 使用环境变量配置作为fallback
            self._api_config = {
                "api_key": settings.LLM_API_KEY,
                "api_base": settings.LLM_API_BASE or "https://api.moonshot.cn/v1",
                "model": settings.LLM_MODEL or "moonshot-v1-8k-vision-preview",
                "temperature": settings.LLM_TEMPERATURE or 0.1,
                "max_tokens": settings.LLM_MAX_TOKENS or 2000
            }
        return self._api_config

    def _get_openai_client(self, config: Dict[str, Any]):
        """获取或创建OpenAI客户端"""
        try:
            from openai import OpenAI
            
            if self._openai_client is None:
                self._openai_client = OpenAI(
                    api_key=config['api_key'],
                    base_url=config['api_base'],
                )
                logger.info("创建OpenAI客户端成功")
            return self._openai_client
        except ImportError as e:
            logger.error(f"未安装openai库: {e}")
            logger.error("请运行: pip install openai")
            return None

    async def recognize_vin(self, image_base64: str) -> Dict[str, Any]:
        """
        使用LLM多模态识别图片中的VIN码
        
        优先使用OpenAI SDK，如果失败则降级到HTTP API

        Args:
            image_base64: Base64编码的图片

        Returns:
            JSON格式的识别结果
        """
        config = await self._get_api_config()
        
        if not config or not config.get("api_key"):
            logger.error("LLM API Key未配置")
            return {
                "vin_code": None,
                "car_model": None,
                "confidence": 0.0,
                "error": "LLM API Key未配置"
            }

        # 尝试使用OpenAI SDK
        openai_client = self._get_openai_client(config)
        if openai_client:
            try:
                return await self._recognize_with_sdk(openai_client, config, image_base64)
            except Exception as e:
                logger.error(f"OpenAI SDK调用失败: {e}")
                logger.info("降级到HTTP API调用")
        
        # 降级到HTTP API
        return await self._recognize_with_http(config, image_base64)

    async def _recognize_with_sdk(self, client, config: Dict[str, Any], image_base64: str) -> Dict[str, Any]:
        """使用OpenAI SDK进行识别
        
        参考Kimi官网示例:
        https://platform.moonshot.cn/docs/guide/use-sdk
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """你是专业VIN识别引擎。规则：
1. 仔细查看图片中的17位车架号（由数字和大写字母组成，不含I、O、Q）
2. **只返回17位VIN码**，禁止任何解释、标点、格式包装
3. 如果看不清或不确定，返回"RECOGNITION_FAILED"
4. 如果图片倾斜或反光，尽力识别最接近VIN标记的那串17位码
5. 绝对不要返回JSON格式或其他格式，只返回纯文本VIN码"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "请识别图片中的17位车架号(VIN)，只返回VIN码本身。"
                        }
                    ]
                }
            ]

            # 使用OpenAI SDK调用
            completion = client.chat.completions.create(
                model=config['model'],
                messages=messages,
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )

            # 解析响应
            raw_result = completion.choices[0].message.content.strip()
            cleaned_vin = self._clean_vin(raw_result)

            logger.info(f"Kimi SDK识别结果: {cleaned_vin}")

            return {
                "vin_code": cleaned_vin,
                "car_model": None,  # LLM识别可能不包含车型
                "confidence": 0.95 if cleaned_vin else 0.0,
                "raw_response": raw_result,
                "method": "kimi_sdk"
            }

        except Exception as e:
            logger.error(f"Kimi SDK调用失败: {e}")
            raise

    async def _recognize_with_http(self, config: Dict[str, Any], image_base64: str) -> Dict[str, Any]:
        """使用HTTP API进行识别（降级方案）"""
        logger.info("使用HTTP API调用Kimi")
        
        messages = [
            {
                "role": "system",
                "content": """你是专业VIN识别引擎。规则：
1. 仔细查看图片中的17位车架号（由数字和大写字母组成，不含I、O、Q）
2. **只返回17位VIN码**，禁止任何解释、标点、格式包装
3. 如果看不清或不确定，返回"RECOGNITION_FAILED"
4. 如果图片倾斜或反光，尽力识别最接近VIN标记的那串17位码
5. 绝对不要返回JSON格式或其他格式，只返回纯文本VIN码"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请识别图片中的17位车架号(VIN)，只返回VIN码本身。"
                    }
                ]
            }
        ]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config['api_base']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": config['model'],
                        "messages": messages,
                        "temperature": config['temperature'],
                        "max_tokens": config['max_tokens']
                    },
                    timeout=60.0
                )

                response.raise_for_status()
                data = response.json()

                # 解析LLM响应
                raw_result = data["choices"][0]["message"]["content"].strip()
                cleaned_vin = self._clean_vin(raw_result)

                logger.info(f"Kimi HTTP识别结果: {cleaned_vin}")

                return {
                    "vin_code": cleaned_vin,
                    "car_model": None,
                    "confidence": 0.95 if cleaned_vin else 0.0,
                    "raw_response": raw_result,
                    "method": "kimi_http"
                }

        except httpx.HTTPError as e:
            logger.error(f"Kimi HTTP API请求失败: {e}")
            return {
                "vin_code": None,
                "car_model": None,
                "confidence": 0.0,
                "error": str(e),
                "method": "kimi_http"
            }
        except Exception as e:
            logger.error(f"Kimi HTTP识别未知错误: {e}")
            return {
                "vin_code": None,
                "car_model": None,
                "confidence": 0.0,
                "error": str(e),
                "method": "kimi_http"
            }

    def _clean_vin(self, text: str) -> Optional[str]:
        """清理并提取17位VIN码"""
        if not text:
            return None

        text = text.upper()

        # 检查失败标记
        if any(mark in text for mark in ['FAIL', 'ERROR', '失败', '错误', '无法', 'NULL', 'RECOGNITION_FAILED']):
            return None

        # 去除所有非字母数字字符
        text = re.sub(r'[^A-Z0-9]', '', text)

        # 提取有效VIN字符（排除I,O,Q）
        valid_chars = re.findall(r'[A-HJ-NPR-Z0-9]', text)
        vin_candidate = ''.join(valid_chars)

        # 严格17位
        if len(vin_candidate) == 17:
            return vin_candidate

        # 尝试从原文中提取17位连续字符
        matches = re.findall(r'[A-HJ-NPR-Z0-9]{17}', text)
        if matches:
            return matches[0]

        return None
