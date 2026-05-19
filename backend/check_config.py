"""
检查 API 配置详细信息
"""
import asyncio
from app.db.session import async_session
from app.services.api_config_service import ApiConfigService

async def check_config():
    """检查 API 配置"""
    try:
        async with async_session() as db:
            service = ApiConfigService(db)
            config = await service.get_default_by_type("llm")
            
            if config:
                print("=" * 60)
                print("LLM 配置详细信息")
                print("=" * 60)
                print(f"配置名称: {config.name}")
                print(f"配置类型: {config.config_type}")
                print(f"API Key: {'已设置' if config.api_key else '未设置'}")
                if config.api_key:
                    print(f"API Key 长度: {len(config.api_key)}")
                    print(f"API Key 前20位: {config.api_key[:20]}...")
                print(f"API Base: {config.api_base}")
                print(f"模型名称: {config.model}")
                print(f"温度参数: {config.temperature}")
                print(f"最大Token: {config.max_tokens}")
                print(f"是否默认: {config.is_default}")
                print(f"是否激活: {config.is_active}")
                print(f"\n提示词模板前200字符:")
                if config.prompt_template:
                    print(config.prompt_template[:200])
                else:
                    print("未设置")
                print("=" * 60)
                
                # 验证配置是否正确
                print("\n配置验证:")
                if not config.api_key:
                    print("❌ API Key 为空")
                elif len(config.api_key) < 40:
                    print(f"❌ API Key 长度异常 ({len(config.api_key)} 字符)")
                else:
                    print("✅ API Key 已设置")
                    
                if not config.api_base:
                    print("❌ API Base 为空")
                elif "moonshot" not in config.api_base:
                    print(f"⚠️ API Base 可能不正确: {config.api_base}")
                else:
                    print("✅ API Base 正确")
                    
                if not config.model:
                    print("❌ 模型名称为空")
                else:
                    print(f"✅ 模型名称: {config.model}")
                    
            else:
                print("❌ 没有找到默认的 LLM 配置")
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_config())
