from typing import Optional, List
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository, UserRepositoryError
from app.models.user_orm import UserOrm, UserStatusEnum, UserRoleEnum
from app.schemas.user import (
    UserRegisterRequest, UserUpdateRequest, UserResponseItem, 
    UserLoginResponse, PasswordChangeRequest, UserItem
)
from app.utils.password_utils import verify_password, get_password_hash
from app.core.token_utils import create_access_token

class UserServiceError(Exception):
    """用户服务异常"""
    pass

class UserService(object):
    # 默认token过期时间 (8小时)
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

    def __init__(self, db_session: AsyncSession):
        self._repository = UserRepository(db_session)
    
    async def register_user(self, user_data: UserRegisterRequest) -> UserResponseItem:
        """注册新用户"""
        try:
            # 检查用户名是否已存在
            existing_user = await self._repository.find_active_by_username(user_data.username)
            if existing_user:
                logger.warning(f"用户注册失败，用户名已存在: {user_data.username}")
                raise UserServiceError("用户名已存在")
            
            # 检查邮箱是否已存在
            existing_email = await self._repository.find_active_by_email(user_data.email)
            if existing_email:
                logger.warning(f"用户注册失败，邮箱已存在: {user_data.email}")
                raise UserServiceError("邮箱已存在")
            
            logger.debug(f"用户唯一性得到检验。创建新用户: {user_data.username}, {user_data.email}")
            # 创建新用户
            hashed_password = get_password_hash(user_data.password)
            user_item = UserItem(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                nickname=user_data.nickname,
            )

            user_orm = user_item.to_orm()
            await self._repository.create_user(user_orm)
            return self._convert_to_response_item(user_orm)

        except UserRepositoryError as e:
            logger.error(f"用户注册时数据库操作失败: {e}")
            raise UserServiceError(f"用户注册失败: {e}")
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"用户注册过程中发生未知错误: {e}")
            raise UserServiceError(f"用户注册过程中发生未知错误: {e}")
    
    async def _authenticate_user(self, username: str, password: str) -> Optional[UserOrm]:
        """验证用户凭据"""
        try:
            user = await self._repository.find_active_by_username(username)
            if not user:
                logger.warning(f"认证失败，用户不存在: {username}")
                raise UserServiceError("用户不存在")
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"认证失败，密码错误: {username}")
                raise UserServiceError("密码错误")
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            await self._repository.update_user(user)
            
            return user
        except UserServiceError:
            raise
        except UserRepositoryError as e:
            logger.error(f"用户认证时数据库操作失败: {e}")
            raise UserServiceError(f"用户认证失败: {e}")
        except Exception as e:
            logger.error(f"用户认证过程中发生未知错误: {e}")
            raise UserServiceError(f"用户认证过程中发生未知错误: {e}")
    
    async def login_user(self, username: str, password: str) -> UserLoginResponse:
        """用户登录并生成访问令牌"""
        try:
            user = await self._authenticate_user(username, password)
            if not user:
                raise UserServiceError("用户名或密码不正确")
            
            # 检查账户状态
            if user.status != UserStatusEnum.enabled:
                logger.warning(f"登录失败，账户状态并非出于正常使用状态: {username}, 当前状态: {user.status}")
                raise UserServiceError(f"账户状态异常: {user.status.value}")
            
            # 生成访问令牌
            expires_delta = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username, "id": user.id},
                expires_delta=expires_delta
            )
            
            # 转换为响应格式
            user_response = self._convert_to_response_item(user)
            
            return UserLoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_response
            )
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"用户登录过程中发生未知错误: {e}")
            raise UserServiceError(f"用户登录失败: {e}")
        
    async def get_user_profile(self, username: str) -> UserResponseItem:
        """获取用户资料"""
        try:
            # 检查用户是否存在
            user = await self._repository.find_active_by_username(username)
            if not user:
                logger.warning(f"获取用户资料失败，用户不存在: {username}")
                raise UserServiceError("用户不存在")
            
            return self._convert_to_response_item(user)
        except UserRepositoryError as e:
            logger.error(f"获取用户资料时数据库操作失败: {e}")
            raise UserServiceError(f"获取用户资料失败: {e}")
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"获取用户资料过程中发生未知错误: {e}")
            raise UserServiceError(f"获取用户资料失败: {e}")
    
    async def update_user_profile(self, username: str, update_data: UserUpdateRequest) -> UserResponseItem:
        """更新用户资料"""
        try:
            # 检查用户是否存在
            user = await self._repository.find_active_by_username(username)
            if not user:
                logger.warning(f"更新失败，用户不存在: 用户名 {username}")
                raise UserServiceError("用户不存在")
            
            # 如果要更新邮箱，检查邮箱是否已被使用
            if update_data.email and update_data.email != user.email:
                existing_email = await self._repository.find_active_by_email(update_data.email)
                if existing_email:
                    logger.warning(f"更新失败，邮箱已存在: {update_data.email}")
                    raise UserServiceError("邮箱已被其他用户使用")
            
            # 更新用户信息
            updated_user = await self._repository.update_user_info(
                username,
                nickname=update_data.nickname,
                email=update_data.email,
                avatar_id=update_data.avatar_id,
                gender=update_data.gender,
                birth_date=update_data.birth_date,
                country=update_data.country
            )
            
            if not updated_user:
                logger.error(f"更新用户信息失败: 用户名 {username}")
                raise UserServiceError("更新用户信息失败")
            
            return self._convert_to_response_item(updated_user)
        except UserRepositoryError as e:
            logger.error(f"更新用户信息时数据库操作失败: {e}")
            raise UserServiceError(f"更新用户信息失败: {e}")
        except UserServiceError:
            # 直接抛出服务异常
            raise
        except Exception as e:
            logger.error(f"更新用户信息过程中发生未知错误: {e}")
            raise UserServiceError(f"更新用户信息失败: {e}")
    
    async def change_password(self, username: str, password_data: PasswordChangeRequest) -> bool:
        """更改用户密码"""
        try:
            # 获取用户信息
            user = await self._repository.find_active_by_username(username)
            if not user:
                logger.warning(f"更改密码失败，用户不存在: 用户名 {username}")
                raise UserServiceError("用户不存在")
            
            # 验证旧密码
            if not verify_password(password_data.old_password, user.hashed_password):
                logger.warning(f"更改密码失败，旧密码不正确: 用户名 {username}")
                raise UserServiceError("旧密码不正确")
            
            # 哈希新密码并更新
            hashed_password = get_password_hash(password_data.new_password)
            user.hashed_password = hashed_password
            await self._repository.update_user(user)
            
            return True
        except UserRepositoryError as e:
            logger.error(f"更改密码时数据库操作失败: {e}")
            raise UserServiceError(f"更改密码失败: {e}")
        except UserServiceError:
            # 直接抛出服务异常
            raise
        except Exception as e:
            logger.error(f"更改密码过程中发生未知错误: {e}")
            raise UserServiceError(f"更改密码失败: {e}")
    
    async def delete_user(self, username: str) -> bool:
        """注销用户（用软删除实现）"""
        try:
            user = await self._repository.find_active_by_username(username)
            if not user:
                logger.warning(f"删除用户失败，用户不存在: 用户名 {username}")
                raise UserServiceError("用户不存在")
            await self._repository.soft_delete(username)
            return True
        except UserRepositoryError as e:
            logger.error(f"删除用户时数据库操作失败: {e}")
            raise UserServiceError(f"删除用户失败: {e}")
        except UserServiceError:
            # 直接抛出服务异常
            raise
        except Exception as e:
            logger.error(f"删除用户过程中发生未知错误: {e}")
            raise UserServiceError(f"删除用户失败: {e}")
    
    @staticmethod
    def _convert_to_response_item(user_orm: UserOrm) -> UserResponseItem:
        """将 ORM 模型转换为响应模型"""
        return UserResponseItem.model_validate(user_orm)


if __name__ == "__main__":
    import asyncio
    from app.core.database import get_async_db
    from app.schemas.user import UserRegisterRequest, UserUpdateRequest, PasswordChangeRequest
    
    # 测试用户信息
    TEST_USERNAME = "testuser"
    TEST_EMAIL = "test@example.com"
    TEST_PASSWORD = "securepassword123"
    NEW_PASSWORD = "newpassword456"
    
    async def test_register_user():
        """测试用户注册功能"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                register_data = UserRegisterRequest(
                    username=TEST_USERNAME,
                    email=TEST_EMAIL,
                    password=TEST_PASSWORD,
                    nickname="测试用户"
                )
                
                new_user = await user_service.register_user(register_data)
                logger.info(f"用户注册成功: 用户名={new_user.username}")
                break
        except UserServiceError as e:
            logger.error(f"用户注册失败: {e}")
        except Exception as e:
            logger.error(f"用户注册过程中发生未知错误: {e}")
    
    async def test_login_user():
        """测试用户登录功能"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                login_result = await user_service.login_user(TEST_USERNAME, TEST_PASSWORD)
                logger.info(f"登录成功: 用户={login_result.user.username}")
                logger.info(f"访问令牌: {login_result.access_token[:15]}...")
                logger.info(f"令牌类型: {login_result.token_type}")
                logger.info(f"过期时间: {login_result.expires_in}秒")
                break
        except UserServiceError as e:
            logger.error(f"登录失败: {e}")
        except Exception as e:
            logger.error(f"登录过程中发生未知错误: {e}")
    
    async def test_update_user_profile():
        """测试更新用户资料功能"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                update_data = UserUpdateRequest(
                    nickname="已更新的测试用户",
                    email="updated@example.com",
                    gender="male",
                    country="中国"
                )
                
                updated_user = await user_service.update_user_profile(TEST_USERNAME, update_data)
                logger.info(f"更新后昵称: {updated_user.nickname}")
                logger.info(f"更新后邮箱: {updated_user.email}")
                logger.info(f"更新后性别: {updated_user.gender}")
                logger.info(f"更新后国家: {updated_user.country}")
                break
        except UserServiceError as e:
            logger.error(f"更新用户资料失败: {e}")
        except Exception as e:
            logger.error(f"更新用户资料过程中发生未知错误: {e}")
    
    async def test_change_password():
        """测试修改密码功能"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                password_data = PasswordChangeRequest(
                    old_password=TEST_PASSWORD,
                    new_password=NEW_PASSWORD
                )
                
                result = await user_service.change_password(TEST_USERNAME, password_data)
                logger.info("密码修改成功")
                break
        except UserServiceError as e:
            logger.error(f"修改密码失败: {e}")
        except Exception as e:
            logger.error(f"修改密码过程中发生未知错误: {e}")
    
    async def test_login_with_new_password():
        """测试用新密码登录"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                login_result = await user_service.login_user(TEST_USERNAME, NEW_PASSWORD)
                logger.info("使用新密码登录成功")
                break
        except UserServiceError as e:
            logger.error(f"使用新密码登录失败: {e}")
        except Exception as e:
            logger.error(f"使用新密码登录过程中发生未知错误: {e}")
    
    async def test_delete_user():
        """测试删除用户功能"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                result = await user_service.delete_user(TEST_USERNAME)
                logger.info(f"用户 {TEST_USERNAME} 删除成功")
                break
        except UserServiceError as e:
            logger.error(f"删除用户失败: {e}")
        except Exception as e:
            logger.error(f"删除用户过程中发生未知错误: {e}")
    
    async def test_login_deleted_user():
        """测试登录已删除的用户"""
        try:
            async for db in get_async_db():
                user_service = UserService(db)
                await user_service.login_user(TEST_USERNAME, NEW_PASSWORD)
                logger.error("错误: 已删除用户仍可登录")
                break
        except UserServiceError as e:
            logger.info(f"预期行为: 已删除用户无法登录 - {e}")
        except Exception as e:
            logger.error(f"登录已删除用户过程中发生未知错误: {e}")
    
    async def main():
        """运行所有测试"""
        logger.info("开始用户服务测试...")
        
        # 测试用户注册
        await test_register_user()
        
        # 测试用户登录
        await test_login_user()
        
        # 测试更新用户资料
        await test_update_user_profile()
        
        # 测试修改密码
        await test_change_password()
        
        # 测试用户登录
        await test_login_user()

        # 测试使用新密码登录
        await test_login_with_new_password()
        
        # 测试删除用户
        await test_delete_user()
        
        # 测试登录已删除用户
        await test_login_deleted_user()
        
        logger.info("用户服务测试完成")

    # 运行测试
    asyncio.run(main())
    