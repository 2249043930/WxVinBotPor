import json
import re
import os
from typing import Dict, Any, Optional
import httpx
from loguru import logger
from app.config import settings
from app.db.session import async_session
from app.services.api_config_service import ApiConfigService


class OCRClient:
    """豆包OCR客户端 - 使用豆包模型进行图片文字识别
    
    支持两种方式调用:
    1. Ark SDK方式 (推荐) - 使用volcenginesdkarkruntime库
    2. HTTP API方式 - 使用httpx直接调用
    """

    def __init__(self):
        self._api_config = None
        self._ark_client = None

    async def _get_api_config(self):
        """从数据库获取豆包OCR API配置"""
        try:
            async with async_session() as db:
                from sqlalchemy import select
                from app.models.api_config import ApiConfig
                
                # 优先查找名称为'doubao'的配置
                result = await db.execute(
                    select(ApiConfig).where(
                        ApiConfig.name.ilike("%doubao%"),
                        ApiConfig.is_active == True,
                        ApiConfig.is_deleted == False
                    )
                )
                config = result.scalar_one_or_none()
                
                if config:
                    # 使用配置的模型，如果没有则使用默认的视觉模型
                    model_name = config.model or "doubao-vision-pro-32k-241115"
                    self._api_config = {
                        "api_key": config.api_key,
                        "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                        "model": model_name,
                    }
                    logger.info(f"从数据库加载豆包OCR配置: {config.name}, 模型: {self._api_config['model']}")
                else:
                    # 使用环境变量配置
                    model_name = settings.DOUBAO_OCR_MODEL or "doubao-vision-pro-32k-241115"
                    self._api_config = {
                        "api_key": settings.DOUBAO_API_KEY,
                        "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                        "model": model_name,
                    }
                    logger.warning("数据库中没有豆包OCR配置，使用环境变量配置")
        except Exception as e:
            logger.error(f"获取豆包OCR配置失败: {e}")
            # 使用环境变量配置作为fallback
            model_name = settings.DOUBAO_OCR_MODEL or "doubao-vision-pro-32k-241115"
            self._api_config = {
                "api_key": settings.DOUBAO_API_KEY,
                "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                "model": model_name,
            }
        return self._api_config

    def _get_ark_client(self, config: Dict[str, str]):
        """获取或创建Ark客户端"""
        try:
            # 使用volcengine-python-sdk的arkruntime模块
            from volcenginesdkarkruntime import Ark
            
            if self._ark_client is None:
                self._ark_client = Ark(
                    base_url=config['api_base'],
                    api_key=config['api_key'],
                )
                logger.info("创建Ark客户端成功")
            return self._ark_client
        except ImportError as e:
            logger.error(f"未安装volcengine-python-sdk[ark]库: {e}")
            logger.error("请运行: pip install 'volcengine-python-sdk[ark]'")
            return None

    async def recognize(self, image_base64: str) -> Dict[str, Any]:
        """
        使用豆包模型OCR识别图片中的VIN码
        
        优先使用Ark SDK，如果失败则降级到HTTP API

        Args:
            image_base64: Base64编码的图片

        Returns:
            识别结果字典
        """
        config = await self._get_api_config()
        
        if not config or not config.get("api_key"):
            logger.error("豆包OCR API Key未配置")
            return {
                "vin_code": None,
                "car_model": None,
                "confidence": 0.0,
                "error": "豆包OCR API Key未配置"
            }

        prompt = self._build_ocr_prompt()

        # 尝试使用Ark SDK
        ark_client = self._get_ark_client(config)
        
        if ark_client:
            try:
                return await self._recognize_with_sdk(ark_client, config, prompt, image_base64)
            except Exception as e:
                logger.error(f"Ark SDK调用失败: {e}")
                logger.info("降级到HTTP API调用")
        
        # 降级到HTTP API
        return await self._recognize_with_http(config, prompt, image_base64)

    async def _recognize_with_sdk(self, ark_client, config: Dict[str, str], prompt: str, image_base64: str) -> Dict[str, Any]:
        """使用Ark SDK进行识别
        
        参考豆包官网示例:
        https://www.volcengine.com/docs/82379/1319847
        
        注意：使用 chat.completions.create 接口，兼容性更好
        """
        try:
            # 使用 chat.completions.create 接口（兼容性更好）
            response = ark_client.chat.completions.create(
                model=config['model'],
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的OCR文字识别助手。请从图片中识别所有文字内容，特别关注车架号(VIN)信息。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )

            logger.info(f"豆包SDK响应类型: {type(response)}")

            # 解析响应
            content = self._parse_sdk_response(response)
            
            logger.info(f"豆包SDK识别内容: {content[:200]}...")

            # 尝试解析 JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # 如果不是 JSON，直接使用文本
                result = {"all_text": content, "vin_code": None}

            # 提取VIN码
            vin_code = self._extract_vin_from_result(result)

            return {
                "vin_code": vin_code,
                "car_model": result.get("car_model"),
                "confidence": result.get("confidence", 0.0),
                "raw_text": result.get("all_text", content),
                "raw_response": content,
                "method": "doubao_sdk"
            }

        except Exception as e:
            logger.error(f"豆包SDK调用失败: {e}")
            raise

    def _parse_sdk_response(self, response) -> str:
        """解析SDK响应，提取内容"""
        try:
            # 尝试不同的响应格式
            if hasattr(response, 'output'):
                # responses格式 - 豆包SDK返回的是对象，有output属性
                output = response.output
                # 如果output是列表，取第一个元素的content
                if isinstance(output, list) and len(output) > 0:
                    if hasattr(output[0], 'content'):
                        return output[0].content
                    elif isinstance(output[0], dict):
                        return output[0].get('content', '')
                elif isinstance(output, str):
                    return output
                else:
                    return str(output)
            elif hasattr(response, 'choices') and response.choices:
                # chat.completions格式
                return response.choices[0].message.content
            elif isinstance(response, dict):
                if "output" in response:
                    return response["output"]
                elif "choices" in response:
                    return response["choices"][0]["message"]["content"]
            else:
                # 转换为字符串
                return str(response)
        except Exception as e:
            logger.error(f"解析SDK响应失败: {e}, 响应类型: {type(response)}")
            return str(response)

    async def _recognize_with_http(self, config: Dict[str, str], prompt: str, image_base64: str) -> Dict[str, Any]:
        """使用HTTP API进行识别（降级方案）"""
        logger.info("使用HTTP API调用豆包OCR")
        
        # 构建豆包 chat.completions 格式的请求
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的OCR文字识别助手。请从图片中识别所有文字内容，特别关注车架号(VIN)信息。"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config['api_base']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=60.0
                )

                response.raise_for_status()
                data = response.json()

                # 解析响应
                if "choices" in data:
                    content = data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"未知的响应格式: {data}")
                    return {
                        "vin_code": None,
                        "car_model": None,
                        "confidence": 0.0,
                        "error": "未知的响应格式",
                        "method": "doubao_http"
                    }

                # 尝试解析 JSON
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    result = {"all_text": content, "vin_code": None}

                # 提取VIN码
                vin_code = self._extract_vin_from_result(result)

                return {
                    "vin_code": vin_code,
                    "car_model": result.get("car_model"),
                    "confidence": result.get("confidence", 0.0),
                    "raw_text": result.get("all_text", content),
                    "raw_response": content,
                    "method": "doubao_http"
                }

        except httpx.HTTPError as e:
            logger.error(f"豆包OCR HTTP API请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"豆包OCR识别未知错误: {e}")
            raise

    def _build_ocr_prompt(self) -> str:
        """构建OCR识别提示词"""
        return """请识别图片中的所有文字内容，并提取车架号(VIN)信息。

要求：
1. 识别图片中的所有可见文字
2. 特别关注17位的车架号(VIN码)，VIN码通常由17位字母和数字组成
3. 如果有车型信息也一并识别
4. 返回严格的JSON格式

返回格式：
{
    "all_text": "图片中识别的所有文字",
    "vin_code": "识别的17位VIN码，如果没有填null",
    "car_model": "车型信息，如：丰田凯美瑞 2.0L",
    "confidence": 0.85,
    "notes": "其他备注"
}

如果图片中没有VIN码，请返回：
{
    "all_text": "识别的文字内容",
    "vin_code": null,
    "car_model": null,
    "confidence": 0,
    "notes": "未找到VIN码"
}"""

    def _extract_vin_from_result(self, result: Dict[str, Any]) -> Optional[str]:
        """从识别结果中提取VIN码"""
        # 优先从vin_code字段获取
        vin_code = result.get("vin_code")
        if vin_code and len(vin_code) == 17:
            return vin_code.upper()

        # 从all_text中匹配
        all_text = result.get("all_text", "")
        pattern = r'[A-HJ-NPR-Z0-9]{17}'
        match = re.search(pattern, all_text.upper().replace(' ', '').replace('-', ''))
        return match.group(0) if match else None
