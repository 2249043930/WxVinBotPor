"""接口配置服务"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.api_config import ApiConfig
from app.schemas.api_config import ApiConfigCreate, ApiConfigUpdate
import httpx
import json
import base64
from datetime import datetime


class ApiConfigService:
    """接口配置服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        config_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取配置列表"""
        query = select(ApiConfig)
        
        if config_type:
            query = query.where(ApiConfig.config_type == config_type)
        
        # 获取总数
        count_result = await self.db.execute(
            select(ApiConfig).where(
                ApiConfig.config_type == config_type if config_type else True
            )
        )
        total = len(count_result.scalars().all())
        
        # 分页
        query = query.order_by(ApiConfig.sort_order, ApiConfig.id)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return {
            "list": items,
            "total": total
        }

    async def get_by_id(self, config_id: int) -> Optional[ApiConfig]:
        """根据ID获取配置"""
        result = await self.db.execute(
            select(ApiConfig).where(ApiConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_default_by_type(self, config_type: str) -> Optional[ApiConfig]:
        """获取默认配置"""
        result = await self.db.execute(
            select(ApiConfig).where(
                and_(
                    ApiConfig.config_type == config_type,
                    ApiConfig.is_default == True,
                    ApiConfig.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, config: ApiConfigCreate) -> ApiConfig:
        """创建配置"""
        # 如果设置为默认，取消其他默认配置
        if config.is_default:
            await self._clear_default(config.config_type)
        
        db_config = ApiConfig(**config.model_dump())
        self.db.add(db_config)
        await self.db.commit()
        await self.db.refresh(db_config)
        return db_config

    async def update(self, config_id: int, config: ApiConfigUpdate) -> Optional[ApiConfig]:
        """更新配置"""
        db_config = await self.get_by_id(config_id)
        if not db_config:
            return None
        
        # 如果设置为默认，取消其他默认配置
        if config.is_default:
            await self._clear_default(db_config.config_type)
        
        update_data = config.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_config)
        return db_config

    async def delete(self, config_id: int) -> bool:
        """删除配置"""
        db_config = await self.get_by_id(config_id)
        if not db_config:
            return False
        
        await self.db.delete(db_config)
        await self.db.commit()
        return True

    async def _clear_default(self, config_type: str):
        """清除默认配置"""
        result = await self.db.execute(
            select(ApiConfig).where(
                and_(
                    ApiConfig.config_type == config_type,
                    ApiConfig.is_default == True
                )
            )
        )
        configs = result.scalars().all()
        for config in configs:
            config.is_default = False
        await self.db.commit()


class VINRecognizer:
    """VIN识别器 - 支持多种LLM"""

    def __init__(self, api_config: ApiConfig):
        self.config = api_config

    def _is_holiday(self) -> tuple[bool, str]:
        """检查是否是节假日"""
        today = datetime.now()
        month = today.month
        day = today.day

        holidays = {
            (1, 1): "元旦",
            (2, 14): "情人节",
            (3, 8): "妇女节",
            (4, 1): "愚人节",
            (5, 1): "劳动节",
            (6, 1): "儿童节",
            (10, 1): "国庆节",
            (12, 25): "圣诞节",
        }

        if (month, day) in holidays:
            return True, holidays[(month, day)]
        return False, ""

    def _get_prompt(self) -> str:
        """获取提示词"""
        is_holiday, holiday_name = self._is_holiday()
        
        holiday_prompt = ""
        if is_holiday:
            holiday_prompt = f"今天是{holiday_name}，请在祝福语中加入节日祝福。"

        base_prompt = self.config.prompt_template or """你是一个专业的VIN（车架号）识别助手。请仔细查看用户提供的图片，识别其中的17位车架号。

规则：
1. VIN码由17位字符组成，包含数字和大写字母（不含I、O、Q）
2. 仔细识别图片中的VIN码，确保准确无误
3. 如果图片中没有VIN码或无法识别，vin字段返回空字符串

{holiday_prompt}

请严格按照以下JSON格式返回结果，不要返回其他内容：
{{
    "vin": "识别出的17位VIN码，如果无法识别则返回空字符串",
    "greeting": "{greeting}"
}}

注意：
- 只返回JSON格式的数据，不要有其他说明文字
- 如果不是节假日，greeting字段必须返回字符串"None"
- 确保JSON格式正确，可以被解析"""

        return base_prompt.format(
            holiday_prompt=holiday_prompt,
            greeting='节日快乐！祝您用车愉快！' if is_holiday else 'None'
        )

    async def recognize_vin(self, image_base64: str) -> Dict[str, Any]:
        """识别VIN码"""
        try:
            # 根据配置类型选择不同的API
            if "kimi" in self.config.name.lower() or "moonshot" in self.config.api_base:
                return await self._recognize_with_kimi(image_base64)
            elif "豆包" in self.config.name.lower() or "volces" in self.config.api_base:
                return await self._recognize_with_doubao(image_base64)
            else:
                # 通用OpenAI兼容接口
                return await self._recognize_with_openai(image_base64)
        except Exception as e:
            return {
                "vin": "",
                "greeting": "None",
                "error": f"识别失败: {str(e)}"
            }

    async def _recognize_with_kimi(self, image_base64: str) -> Dict[str, Any]:
        """使用Kimi识别"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.model or "moonshot-v1-8k-vision-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_prompt()
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
                                    "text": "请识别这张图片中的VIN码，按JSON格式返回结果。"
                                }
                            ]
                        }
                    ],
                    "temperature": float(self.config.temperature or 0.1),
                    "max_tokens": self.config.max_tokens or 2000
                },
                timeout=30.0
            )

            return self._parse_response(response)

    async def _recognize_with_doubao(self, image_base64: str) -> Dict[str, Any]:
        """使用豆包识别"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.model or "doubao-pro-32k",
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_prompt()
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
                                    "text": "请识别这张图片中的VIN码，按JSON格式返回结果。"
                                }
                            ]
                        }
                    ],
                    "temperature": float(self.config.temperature or 0.1),
                    "max_tokens": self.config.max_tokens or 2000
                },
                timeout=30.0
            )

            return self._parse_response(response)

    async def _recognize_with_openai(self, image_base64: str) -> Dict[str, Any]:
        """使用通用OpenAI接口识别"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.model or "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_prompt()
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
                                    "text": "请识别这张图片中的VIN码，按JSON格式返回结果。"
                                }
                            ]
                        }
                    ],
                    "temperature": float(self.config.temperature or 0.1),
                    "max_tokens": self.config.max_tokens or 2000
                },
                timeout=30.0
            )

            return self._parse_response(response)

    def _parse_response(self, response) -> Dict[str, Any]:
        """解析API响应"""
        if response.status_code != 200:
            return {
                "vin": "",
                "greeting": "None",
                "error": f"API调用失败: {response.status_code}"
            }

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            # 清理可能的markdown代码块
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)

            # 验证必要字段
            if "vin" not in result:
                result["vin"] = ""
            if "greeting" not in result:
                result["greeting"] = "None"

            # 清理VIN码
            vin = result["vin"].strip().upper()
            vin = ''.join(c for c in vin if c.isalnum())
            if len(vin) == 17:
                result["vin"] = vin
            else:
                result["vin"] = ""

            return result

        except json.JSONDecodeError:
            # 如果无法解析JSON，尝试直接提取VIN
            import re
            vin_match = re.search(r'[A-HJ-NPR-Z0-9]{17}', content.upper())
            if vin_match:
                return {
                    "vin": vin_match.group(0),
                    "greeting": "None"
                }
            else:
                return {
                    "vin": "",
                    "greeting": "None",
                    "error": "无法解析返回结果"
                }
