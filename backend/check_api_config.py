"""
检查API配置
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from app.services.api_config_service import ApiConfigService


async def check_api_config():
    """检查API配置"""
    async with async_session() as db:
        service = ApiConfigService(db)

        # 检查LLM配置
        llm_config = await service.get_default_by_type("llm")
        if llm_config:
            print(f"LLM配置: {llm_config.name}")
            print(f"  API Key: {llm_config.api_key[:10]}..." if llm_config.api_key else "  API Key: 未设置")
            print(f"  API Base: {llm_config.api_base}")
            print(f"  Model: {llm_config.model}")
        else:
            print("LLM配置: 未找到")

        # 检查VIN API配置
        vin_config = await service.get_default_by_type("vin")
        if vin_config:
            print(f"\nVIN API配置: {vin_config.name}")
            print(f"  API Key: {vin_config.api_key[:10]}..." if vin_config.api_key else "  API Key: 未设置")
        else:
            print("\nVIN API配置: 未找到")

        # 检查OCR配置
        ocr_config = await service.get_default_by_type("ocr")
        if ocr_config:
            print(f"\nOCR配置: {ocr_config.name}")
            print(f"  API Key: {ocr_config.api_key[:10]}..." if ocr_config.api_key else "  API Key: 未设置")
        else:
            print("\nOCR配置: 未找到")


if __name__ == "__main__":
    asyncio.run(check_api_config())
