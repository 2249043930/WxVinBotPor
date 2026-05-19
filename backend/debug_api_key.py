"""
调试 API Key 加载
"""
import asyncio
from app.db.session import async_session
from app.services.api_config_service import ApiConfigService
from app.modules.vin.llm_client import LLMClient

async def debug_api_key():
    """调试 API Key 加载"""
    try:
        # 直接测试 LLMClient
        client = LLMClient()
        config = await client._get_api_config()
        
        print("=" * 60)
        print("LLMClient 获取的配置:")
        print("=" * 60)
        print(f"API Key: {'已设置' if config.get('api_key') else '未设置'}")
        if config.get('api_key'):
            print(f"API Key 前30位: {config.get('api_key')[:30]}...")
            print(f"API Key 长度: {len(config.get('api_key'))}")
        print(f"API Base: {config.get('api_base')}")
        print(f"Model: {config.get('model')}")
        
        # 直接从数据库获取
        print("\n" + "=" * 60)
        print("直接从数据库获取:")
        print("=" * 60)
        async with async_session() as db:
            service = ApiConfigService(db)
            db_config = await service.get_default_by_type("llm")
            if db_config:
                print(f"配置名称: {db_config.name}")
                print(f"API Key: {'已设置' if db_config.api_key else '未设置'}")
                if db_config.api_key:
                    print(f"API Key 前30位: {db_config.api_key[:30]}...")
                    print(f"API Key 长度: {len(db_config.api_key)}")
            else:
                print("没有找到配置！")
                
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_api_key())
