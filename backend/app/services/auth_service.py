from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user_crud
from app.crud.log import log_crud
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas.auth import Token
from app.models.user import User


class AuthService:
    """认证服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, username: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """验证用户
        
        Returns:
            tuple: (user, error_message)
            - user: 验证成功返回用户对象，失败返回None
            - error_message: 失败时返回错误信息，成功返回None
        """
        user = await user_crud.get_by_username(self.db, username)
        if not user:
            return None, "用户名或密码错误"
        if not verify_password(password, user.password_hash):
            return None, "用户名或密码错误"
        if not user.is_active:
            return None, "账户已被禁用"
        return user, None

    async def log_login(self, user: User, ip_address: str = None, user_agent: str = None):
        """记录登录日志"""
        log_data = {
            "user_id": user.id,
            "nickname": user.nickname,
            "ip_address": ip_address,
            "login_time": datetime.utcnow(),
            "os": self._parse_os(user_agent),
            "browser": self._parse_browser(user_agent)
        }
        await log_crud.create(self.db, obj_in=log_data)

    def _parse_os(self, user_agent: str) -> str:
        """解析操作系统"""
        if not user_agent:
            return "Unknown"
        if "Windows" in user_agent:
            return "Windows"
        elif "Mac" in user_agent:
            return "MacOS"
        elif "Linux" in user_agent:
            return "Linux"
        elif "Android" in user_agent:
            return "Android"
        elif "iPhone" in user_agent or "iPad" in user_agent:
            return "iOS"
        return "Unknown"

    def _parse_browser(self, user_agent: str) -> str:
        """解析浏览器"""
        if not user_agent:
            return "Unknown"
        if "Chrome" in user_agent:
            return "Chrome"
        elif "Firefox" in user_agent:
            return "Firefox"
        elif "Safari" in user_agent:
            return "Safari"
        elif "Edge" in user_agent:
            return "Edge"
        return "Unknown"

    async def logout(self, token: str):
        """用户登出（可以在这里实现token黑名单）"""
        # TODO: 实现token黑名单
        pass

    async def get_current_user(self, token: str) -> Optional[User]:
        """获取当前用户"""
        from jose import jwt, JWTError
        from app.config import settings

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None

        user = await user_crud.get(self.db, id=int(user_id))
        return user

    def create_access_token(self, user_id: int) -> str:
        """创建访问令牌"""
        return create_access_token(user_id)
