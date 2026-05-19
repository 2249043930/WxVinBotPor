from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user_crud
from app.crud.account import account_crud
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate, UserList
from app.models.user import User


class UserService:
    """用户服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserList:
        """获取用户列表"""
        skip = (page - 1) * page_size
        users, total = await user_crud.search_users(
            self.db,
            keyword=keyword,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )

        return UserList(
            list=users,
            total=total,
            page=page,
            page_size=page_size
        )

    async def create(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing = await user_crud.get_by_username(self.db, user_data.username)
        if existing:
            raise ValueError("用户名已存在")

        # 检查邮箱是否已存在
        if user_data.email:
            existing_email = await user_crud.get_by_email(self.db, user_data.email)
            if existing_email:
                raise ValueError("邮箱已存在")

        # 检查手机号是否已存在
        if user_data.phone:
            existing_phone = await user_crud.get_by_phone(self.db, user_data.phone)
            if existing_phone:
                raise ValueError("手机号已存在")

        # 创建用户
        user_dict = user_data.model_dump()
        password = user_dict.pop("password")
        user_dict["password_hash"] = get_password_hash(password)

        user = await user_crud.create(self.db, obj_in=user_dict)

        # 创建账户记录
        await account_crud.create(self.db, obj_in={"user_id": user.id})

        return user

    async def update(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户"""
        user = await user_crud.get(self.db, id=user_id)
        if not user:
            raise ValueError("用户不存在")

        update_dict = user_data.model_dump(exclude_unset=True)
        user = await user_crud.update(self.db, db_obj=user, obj_in=update_dict)
        return user

    async def delete(self, user_id: int):
        """删除用户"""
        user = await user_crud.get(self.db, id=user_id)
        if not user:
            raise ValueError("用户不存在")

        await user_crud.delete(self.db, id=user_id)

    async def reset_password(self, user_id: int, new_password: str) -> User:
        """重置密码"""
        user = await user_crud.get(self.db, id=user_id)
        if not user:
            raise ValueError("用户不存在")

        update_dict = {"password_hash": get_password_hash(new_password)}
        user = await user_crud.update(self.db, db_obj=user, obj_in=update_dict)
        return user
