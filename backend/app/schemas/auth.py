from pydantic import BaseModel


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str
