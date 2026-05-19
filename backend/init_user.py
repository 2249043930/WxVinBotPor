"""
初始化用户脚本
创建默认管理员账户
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.user import UserCreate


async def init_admin_user():
    """创建默认管理员账户"""
    # 创建引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # 检查是否已存在用户
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.is_deleted == False).limit(1))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("数据库中已存在用户，跳过初始化")
                return
            
            # 创建管理员用户 - 使用UserCreate验证
            user_in = UserCreate(
                username="admin",
                nickname="管理员",
                password="admin123",  # UserCreate需要password字段
                phone="",
                email="",
                is_active=True,
                is_superuser=True,
                remark="系统初始化创建的管理员账户"
            )
            
            # 转换为字典并添加password_hash
            user_data = user_in.model_dump()
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
            
            # 创建用户对象
            user = User(**user_data)
            db.add(user)
            
            # 提交事务
            await db.commit()
            await db.refresh(user)
            
            print(f"管理员账户创建成功！")
            print(f"用户名: {user.username}")
            print(f"昵称: {user.nickname}")
            print(f"密码: admin123")
            print(f"请登录后及时修改密码！")
            
        except Exception as e:
            await db.rollback()
            print(f"创建用户失败: {e}")
            raise
        finally:
            await db.close()
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_admin_user())
