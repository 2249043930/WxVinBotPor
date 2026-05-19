from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "WxVinBot Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置 - 仅使用MySQL
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/wxvinbot"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # LLM配置 - 默认使用Moonshot/Kimi
    LLM_API_KEY: str = ""
    LLM_API_BASE: str = "https://api.moonshot.cn/v1"
    LLM_MODEL: str = "moonshot-v1-8k-vision-preview"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 50
    LLM_PROMPT_TEMPLATE: str = ""

    # 豆包OCR配置
    DOUBAO_API_KEY: str = ""
    DOUBAO_API_BASE: str = "https://ark.cn-beijing.volces.com/api/v3"
    DOUBAO_OCR_MODEL: str = "doubao-vision-pro-32k"
    DOUBAO_MAX_TOKENS: int = 2000

    # 极速数据VIN查询API配置
    VIN_API_KEY: str = ""
    VIN_API_BASE: str = "https://api.jisuapi.com/vin/query"

    # 千寻por微信配置
    QIANXUN_API_URL: str = "http://127.0.0.1:7777"
    QIANXUN_WS_URL: str = "ws://127.0.0.1:7778"
    QIANXUN_WX_ID: str = "wxid_nwrplpmxrwyq22"
    QIANXUN_AUTO_LOGIN: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置（单例）"""
    return Settings()


settings = get_settings()
