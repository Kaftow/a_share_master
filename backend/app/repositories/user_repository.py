from app.models.user_orm import UserOrm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from loguru import logger

class UserRepositoryError(Exception):
    """用于处理用户数据存取过程中出现的异常"""
    pass

class UserRepository:
    """用户数据仓库"""
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_user(self, user: UserOrm) -> None:
        """创建新用户"""
        try:
            self._db.add(user)
            await self._db.commit()
            await self._db.refresh(user)
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"创建用户时发生错误: {e}")
            raise UserRepositoryError("创建用户时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"创建用户时发生未知错误: {e}")
            raise UserRepositoryError("创建用户时发生未知错误", e)

    async def find_active_by_id(self, user_id: int) -> Optional[UserOrm]:
        """通过ID查询用户"""
        try:
            stmt = select(UserOrm).where(
                UserOrm.id == user_id,
                UserOrm.deleted_at.is_(None)
            )
            result = await self._db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"通过ID查询用户时发生错误: {e}")
            raise UserRepositoryError("查询用户时数据库操作失败", e)

    async def find_active_by_username(self, username: str) -> Optional[UserOrm]:
        """通过用户名查询用户"""
        try:
            stmt = select(UserOrm).where(
                UserOrm.username == username,
                UserOrm.deleted_at.is_(None)
            )
            result = await self._db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"通过用户名查询用户时发生错误: {e}")
            raise UserRepositoryError("查询用户时数据库操作失败", e)

    async def find_active_by_email(self, email: str) -> Optional[UserOrm]:
        """通过邮箱查询用户"""
        try:
            stmt = select(UserOrm).where(
                UserOrm.email == email,
                UserOrm.deleted_at.is_(None)
            )
            result = await self._db.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"通过邮箱查询用户时发生错误: {e}")
            raise UserRepositoryError("查询用户时数据库操作失败", e)

    async def update_user(self, user: UserOrm) -> None:
        """更新用户信息"""
        try:
            await self._db.merge(user)
            await self._db.commit()
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"更新用户信息时发生错误: {e}")
            raise UserRepositoryError("更新用户信息时数据库操作失败", e)

    async def soft_delete(self, username: str) -> None:
        """软删除用户"""
        try:
            stmt = update(UserOrm).where(
                UserOrm.username == username,
                UserOrm.deleted_at.is_(None)
            ).values(deleted_at=datetime.now())
            await self._db.execute(stmt)
            await self._db.commit()
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"软删除用户时发生错误: {e}")
            raise UserRepositoryError("软删除用户时数据库操作失败", e)

    async def find_all_active_users(self) -> List[UserOrm]:
        """查询所有活跃用户"""
        try:
            stmt = select(UserOrm).where(UserOrm.deleted_at.is_(None))
            result = await self._db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"查询所有活跃用户时发生错误: {e}")
            raise UserRepositoryError("查询用户时数据库操作失败", e)
        
    async def update_user_info(self, username: str, **kwargs) -> Optional[UserOrm]:
        """
        更新用户特定字段信息
        支持的字段：nickname, email, avatar, gender, birth_date, country, status
        """
        try:
            # 过滤掉不允许更新的字段
            allowed_fields = {
                'nickname', 'email', 'avatar', 'gender', 
                'birth_date', 'country', 'status'
            }
            update_data = {
                k: v for k, v in kwargs.items() 
                if k in allowed_fields and v is not None
            }
            
            if not update_data:
                logger.info("没有提供可更新的字段")
                return await self.find_active_by_username(username)
                
            # 更新时间戳
            update_data['updated_at'] = datetime.now()
            
            # 执行更新
            stmt = (
                update(UserOrm)
                .where(UserOrm.username == username, UserOrm.deleted_at.is_(None))
                .values(**update_data)
            )
            
            await self._db.execute(stmt)
            await self._db.commit()
            
            # 单独查询并返回更新后的用户信息
            return await self.find_active_by_username(username)
            
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"更新用户信息时发生错误: {e}")
            raise UserRepositoryError("更新用户信息时数据库操作失败", e)

if __name__ == "__main__":
    from app.core.database import get_async_db
    import asyncio
    from app.models.user_orm import UserStatusEnum, UserRoleEnum

    async def test_create_user():
        """测试创建用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                test_user = UserOrm(
                    username="testuser",
                    email="test@example.com",
                    hashed_password="hashed_password",
                    nickname="Test User",
                    status=UserStatusEnum.active,
                    role=UserRoleEnum.user
                )
                await repository.create_user(test_user)
                logger.info("用户创建成功")
        except Exception as e:
            logger.error(f"测试创建用户时发生错误: {e}")

    async def test_find_by_username():
        """测试通过用户名查询用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_username("testuse")
                logger.info(f"查询到用户: {user}")
                return user
        except Exception as e:
            logger.error(f"测试查询用户时发生错误: {e}")

    async def test_find_by_email():
        """测试通过邮箱查询用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_email("test@example.com")
                logger.info(f"通过邮箱查询到用户: {user}")
        except Exception as e:
            logger.error(f"测试通过邮箱查询用户时发生错误: {e}")

    async def test_update_user():
        """测试更新用户信息"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_username("testuser")
                if user:
                    user.nickname = "Updated Test User"
                    await repository.update_user(user)
                    logger.info("用户更新成功")
        except Exception as e:
            logger.error(f"测试更新用户时发生错误: {e}")

    async def test_update_user_info():
        """测试更新用户特定字段"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_username("testuse")
                if user:
                    updated_user = await repository.update_user_info(
                        user.id,
                        nickname="新昵称",
                        country="中国",
                        gender="M"
                    )
                    logger.info(f"更新后的用户信息: {updated_user}")
        except Exception as e:
            logger.error(f"测试更新用户特定字段时发生错误: {e}")

    async def test_soft_delete():
        """测试软删除用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_username("testuser")
                if user:
                    await repository.soft_delete(user.id)
                    logger.info("用户软删除成功")
        except Exception as e:
            logger.error(f"测试软删除用户时发生错误: {e}")

    async def test_find_by_id():
        """测试通过ID查询用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                user = await repository.find_active_by_username("testuser")
                if user:
                    found_user = await repository.find_active_by_id(user.id)
                    logger.info(f"通过ID查询到用户: {found_user}")
        except Exception as e:
            logger.error(f"测试通过ID查询用户时发生错误: {e}")

    async def test_find_all_active_users():
        """测试查询所有活跃用户"""
        try:
            async for db in get_async_db():
                repository = UserRepository(db)
                active_users = await repository.find_all_active_users()
                logger.info(f"活跃用户数量: {len(active_users)}")
        except Exception as e:
            logger.error(f"测试查询所有活跃用户时发生错误: {e}")
    
    async def main():
        """运行所有测试"""
        try:
            # 创建新用户
            await test_create_user()
            
            # 测试各种查询方法
            await test_find_by_username()
            await test_find_by_email()
            await test_find_by_id()
            
            # 测试更新方法
            await test_update_user()
            await test_update_user_info()
            
            # 测试查询所有活跃用户
            await test_find_all_active_users()
            
            # 测试软删除用户
            await test_soft_delete()
            
            # 再次测试查询所有活跃用户(应该为0)
            await test_find_all_active_users()
            
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()

    # 执行测试
    asyncio.run(main())