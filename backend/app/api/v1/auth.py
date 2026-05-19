from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求体"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 0
    message: str = "success"
    data: dict


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录 - 会话保持
    
    请求体: {"username": "xxx", "password": "xxx"}
    """
    auth_service = AuthService(db)
    
    user, error_message = await auth_service.authenticate(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "登录失败",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌（会话保持）
    access_token = auth_service.create_access_token(user.id)

    # 记录登录日志
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await auth_service.log_login(user, client_ip, user_agent)

    # 返回前端期望的格式
    return {
        "code": 0,
        "message": "登录成功",
        "data": {
            "token": access_token,
            "userInfo": {
                "id": user.id,
                "nickname": user.nickname,
                "username": user.username,
                "avatar": None,
                "roles": ["admin"] if user.is_superuser else ["user"]
            }
        }
    }


@router.post("/logout")
async def logout():
    """用户登出"""
    # TODO: 实现token黑名单
    return {"code": 0, "message": "登出成功", "data": None}


@router.get("/info")
async def get_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息 - 账户验证"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": current_user.id,
            "nickname": current_user.nickname,
            "username": current_user.username,
            "avatar": None,
            "roles": ["admin"] if current_user.is_superuser else ["user"]
        }
    }
