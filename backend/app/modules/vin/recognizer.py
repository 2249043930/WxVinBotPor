import base64
from typing import Dict, Any, Optional, List
from loguru import logger
from app.modules.vin.llm_client import LLMClient
from app.modules.vin.ocr_client import OCRClient
from app.modules.vin.image_processor import ImageProcessor
from app.db.session import async_session
from app.services.api_config_service import ApiConfigService


class VinRecognizer:
    """车架号识别器 - 支持多模型自动切换
    
    识别策略：
    1. 优先使用配置的默认模型（Kimi/豆包）
    2. 如果失败或置信度低，自动切换到备用模型
    3. 支持模型优先级配置
    """

    def __init__(self):
        self.llm_client = LLMClient()
        self.ocr_client = OCRClient()
        self.image_processor = ImageProcessor()

    async def recognize(
        self, 
        image_data: bytes,
        preferred_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        识别图片中的车架号
        
        识别流程：
        1. 优先使用指定的方法（如果提供）
        2. 否则优先使用LLM多模态识别
        3. LLM失败时 fallback 到豆包OCR
        4. 如果都失败，返回错误

        Args:
            image_data: 图片二进制数据
            preferred_method: 首选识别方法 ('kimi', 'doubao', None)

        Returns:
            {
                "vin_code": "识别的VIN码",
                "car_model": "车型信息",
                "confidence": 置信度,
                "success": 是否成功,
                "method": "识别方法：kimi_sdk/kimi_http/doubao_sdk/doubao_http"
            }
        """
        try:
            # 1. 图片预处理
            processed_image = await self.image_processor.process(image_data)

            # 2. 根据首选方法或默认策略进行识别
            methods_to_try = self._get_methods_order(preferred_method)
            
            last_error = None
            for method in methods_to_try:
                try:
                    result = await self._recognize_with_method(processed_image, method)
                    
                    # 验证结果
                    if self._validate_vin_result(result):
                        result["success"] = True
                        await self._update_stats(success=True, method=method)
                        logger.info(f"VIN识别成功，使用方法: {method}, VIN: {result.get('vin_code')}")
                        return result
                    else:
                        logger.warning(f"方法 {method} 识别结果无效，尝试下一个方法")
                        
                except Exception as e:
                    logger.error(f"方法 {method} 识别失败: {e}")
                    last_error = e
                    continue

            # 3. 所有方法都失败
            await self._update_stats(success=False, method="all_failed")
            return {
                "success": False,
                "method": "none",
                "error": f"所有识别方法均失败，最后错误: {str(last_error)}"
            }

        except Exception as e:
            logger.error(f"VIN识别失败: {e}")
            await self._update_stats(success=False, method="exception")
            return {"success": False, "error": str(e)}

    def _get_methods_order(self, preferred_method: Optional[str]) -> List[str]:
        """获取识别方法的尝试顺序"""
        all_methods = ['kimi_sdk', 'kimi_http', 'doubao_sdk', 'doubao_http']
        
        if preferred_method == 'kimi':
            return ['kimi_sdk', 'kimi_http', 'doubao_sdk', 'doubao_http']
        elif preferred_method == 'doubao':
            return ['doubao_sdk', 'doubao_http', 'kimi_sdk', 'kimi_http']
        else:
            # 默认顺序：优先Kimi，然后豆包
            return ['kimi_sdk', 'kimi_http', 'doubao_sdk', 'doubao_http']

    async def _recognize_with_method(self, image_base64: str, method: str) -> Dict[str, Any]:
        """使用指定方法进行识别"""
        if method in ['kimi_sdk', 'kimi_http']:
            result = await self.llm_client.recognize_vin(image_base64)
            # 确保方法标记正确
            if 'method' not in result:
                result['method'] = method
            return result
        elif method in ['doubao_sdk', 'doubao_http']:
            result = await self.ocr_client.recognize(image_base64)
            # 确保方法标记正确
            if 'method' not in result:
                result['method'] = method
            return result
        else:
            raise ValueError(f"未知的识别方法: {method}")

    async def recognize_with_auto_switch(
        self, 
        image_data: bytes,
        min_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        智能识别，自动切换模型直到获得高置信度结果
        
        Args:
            image_data: 图片二进制数据
            min_confidence: 最小置信度阈值
            
        Returns:
            识别结果
        """
        try:
            # 图片预处理
            processed_image = await self.image_processor.process(image_data)

            # 尝试所有方法，直到获得满足置信度要求的结果
            methods = ['kimi_sdk', 'doubao_sdk', 'kimi_http', 'doubao_http']
            
            for method in methods:
                try:
                    logger.info(f"尝试使用 {method} 进行识别...")
                    
                    if 'kimi' in method:
                        result = await self.llm_client.recognize_vin(processed_image)
                    else:
                        result = await self.ocr_client.recognize(processed_image)
                    
                    # 检查是否成功且置信度满足要求
                    if (self._validate_vin_result(result) and 
                        result.get('confidence', 0) >= min_confidence):
                        result["success"] = True
                        result["method"] = method
                        logger.info(f"识别成功！方法: {method}, 置信度: {result.get('confidence')}")
                        return result
                    else:
                        logger.warning(f"{method} 识别结果置信度不足或无效，继续尝试其他方法")
                        
                except Exception as e:
                    logger.error(f"{method} 识别失败: {e}")
                    continue

            # 如果没有高置信度结果，返回最后一次尝试的结果（如果有）
            logger.warning("未获得高置信度结果，返回最佳尝试")
            return {
                "success": False,
                "method": "none",
                "error": "未获得满足置信度要求的识别结果"
            }

        except Exception as e:
            logger.error(f"智能识别失败: {e}")
            return {"success": False, "error": str(e)}

    async def recognize_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        从文件识别图片中的车架号

        Args:
            image_path: 图片文件路径

        Returns:
            {
                "vin": "识别的VIN码",
                "greeting": "节日祝福语",
                "success": 是否成功,
                "error": 错误信息
            }
        """
        try:
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 调用识别方法
            result = await self.recognize(image_data)

            # 转换返回格式
            if result.get("success"):
                return {
                    "vin": result.get("vin_code", ""),
                    "greeting": result.get("greeting", "None"),
                    "success": True,
                    "method": result.get("method", "unknown")
                }
            else:
                return {
                    "vin": "",
                    "greeting": "None",
                    "success": False,
                    "error": result.get("error", "识别失败")
                }

        except FileNotFoundError:
            logger.error(f"图片文件不存在: {image_path}")
            return {
                "vin": "",
                "greeting": "None",
                "success": False,
                "error": f"图片文件不存在: {image_path}"
            }
        except Exception as e:
            logger.error(f"从文件识别VIN失败: {e}")
            return {
                "vin": "",
                "greeting": "None",
                "success": False,
                "error": str(e)
            }

    def _validate_vin_result(self, result: Dict[str, Any]) -> bool:
        """检测返回值是否准确"""
        vin_code = result.get("vin_code")
        if not vin_code or len(vin_code) != 17:
            return False
        return self._validate_vin_checksum(vin_code)

    def _validate_vin_checksum(self, vin_code: str) -> bool:
        """验证VIN码校验位"""
        if len(vin_code) != 17:
            return False

        # VIN校验位验证（第9位）
        weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
        transliterations = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
            'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
        }

        try:
            total = 0
            for i, char in enumerate(vin_code.upper()):
                if char.isdigit():
                    value = int(char)
                elif char in transliterations:
                    value = transliterations[char]
                else:
                    return False
                total += value * weights[i]

            check_digit = total % 11
            if check_digit == 10:
                check_digit = 'X'
            else:
                check_digit = str(check_digit)

            return vin_code[8].upper() == str(check_digit).upper()

        except Exception:
            return False

    async def _update_stats(self, success: bool, method: str):
        """更新识别统计"""
        # TODO: 实现统计更新逻辑
        pass

    async def get_available_models(self) -> Dict[str, Any]:
        """获取可用的识别模型列表"""
        models = {
            "kimi": {
                "name": "Kimi (Moonshot)",
                "methods": ["kimi_sdk", "kimi_http"],
                "description": "月之暗面多模态大模型",
                "available": False
            },
            "doubao": {
                "name": "豆包 (Volcengine)",
                "methods": ["doubao_sdk", "doubao_http"],
                "description": "字节跳动豆包视觉模型",
                "available": False
            }
        }
        
        try:
            async with async_session() as db:
                service = ApiConfigService(db)
                
                # 检查Kimi配置
                kimi_config = await service.get_default_by_type("llm")
                if kimi_config and kimi_config.api_key:
                    models["kimi"]["available"] = True
                    models["kimi"]["model"] = kimi_config.model
                
                # 检查豆包配置
                from sqlalchemy import select
                from app.models.api_config import ApiConfig
                result = await db.execute(
                    select(ApiConfig).where(
                        ApiConfig.name.ilike("%doubao%"),
                        ApiConfig.is_active == True,
                        ApiConfig.is_deleted == False
                    )
                )
                doubao_config = result.scalar_one_or_none()
                if doubao_config and doubao_config.api_key:
                    models["doubao"]["available"] = True
                    models["doubao"]["model"] = doubao_config.model
                    
        except Exception as e:
            logger.error(f"获取可用模型列表失败: {e}")
        
        return models
