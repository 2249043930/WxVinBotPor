"""
检查豆包配置
"""
import asyncio
from app.db.session import async_session
from sqlalchemy import select
from app.models.api_config import ApiConfig

async def check_doubao_config():
    """检查豆包配置"""
    try:
        async with async_session() as db:
            result = await db.execute(
                select(ApiConfig).where(
                    ApiConfig.name.ilike("%doubao%"),
                    ApiConfig.is_active == True,
                    ApiConfig.is_deleted == False
                )
            )
            config = result.scalar_one_or_none()
            
            if config:
                print("=" * 60)
                print("豆包配置信息")
                print("=" * 60)
                print(f"配置名称: {config.name}")
                print(f"配置类型: {config.config_type}")
                print(f"API Key: {'已设置' if config.api_key else '未设置'}")
                if config.api_key:
                    print(f"API Key 前30位: {config.api_key[:30]}...")
                print(f"API Base: {config.api_base}")
                print(f"模型: {config.model}")
                print(f"是否默认: {config.is_default}")
                print(f"是否激活: {config.is_active}")
                print("=" * 60)
                
                # 检查API地址是否正确
                if "moonshot" in (config.api_base or "").lower():
                    print("\n❌ 错误：API地址使用了 Moonshot 的地址！")
                    print("豆包应该使用: https://ark.cn-beijing.volces.com/api/v3")
                elif "volces" in (config.api_base or "").lower():
                    print("\n✅ API地址正确（火山引擎）")
                else:
                    print(f"\n⚠️ API地址: {config.api_base}")
            else:
                print("❌ 没有找到豆包配置")
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_doubao_config())
