from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.services.user_service import UserService, UserServiceError
from app.core.database import get_async_db
from app.schemas.api_response import APIResponse
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserUpdateRequest,
    PasswordChangeRequest)
from app.utils.response_utils import success_response, error_response
from app.utils.auth_utils import get_current_username

class AuthError(Exception):
    pass

router = APIRouter(prefix="/user", tags=["用户相关接口"])

async def get_user_service(
    db_session: AsyncSession = Depends(get_async_db)
) -> UserService:
    return UserService(db_session)

@router.post("/register", response_model=APIResponse)
async def register_user(
    request: UserRegisterRequest = Body(...),
    service: UserService = Depends(get_user_service)
):
    """
    用户注册
    - request: UserRegisterRequest 包含用户名、密码、邮箱等注册信息
    - service: UserService 作为依赖注入
    """
    try:
        user = await service.register_user(request)
        logger.info(f"用户注册成功: {user.username}")
        return success_response(data=user,message="用户注册成功")
    except UserServiceError as e:
        logger.error(f"用户注册失败: {e}")
        return error_response(error=e,message="用户注册失败")
    except Exception as e:
        logger.error(f"用户注册过程中发生未知错误: {e}")
        return error_response(e)


@router.post("/login", response_model=APIResponse)
async def login_user(
    request: UserLoginRequest = Body(...),
    service: UserService = Depends(get_user_service)
):
    """
    用户登录
    - request: UserLoginRequest 包含用户名和密码
    - service: UserService 作为依赖注入
    """
    try:
        login_result = await service.login_user(request.username, request.password)
        logger.info(f"用户登录成功: {request.username}")
        return success_response(data=login_result, message="登录成功")
    except UserServiceError as e:
        logger.error(f"用户登录失败: {e}")
        return error_response(error=e, message="登录失败")
    except Exception as e:
        logger.error(f"用户登录过程中发生未知错误: {e}")
        return error_response(e)

@router.post("/profile/view", response_model=APIResponse)
async def get_profile(
    username: str = Depends(get_current_username),
    service: UserService = Depends(get_user_service)
):
    """
    获取用户资料
    - username: 要查询的用户名
    - service: UserService 作为依赖注入
    """
    if not username:
        logger.error("用户未登录！")
        return error_response(error=AuthError("用户未登录！"), message="用户未登录！")
    try:
        user_profile = await service.get_user_profile(username)
        logger.info(f"用户资料获取成功: {username}")
        return success_response(data=user_profile, message="资料获取成功")
    except UserServiceError as e:
        logger.error(f"用户资料获取失败: {e}")
        return error_response(error=e, message="资料获取失败")
    except Exception as e:
        logger.error(f"用户资料获取过程中发生未知错误: {e}")
        return error_response(e)
    
@router.post("/profile/update", response_model=APIResponse)
async def update_profile(
    username: str = Depends(get_current_username),
    request: UserUpdateRequest = Body(...),
    service: UserService = Depends(get_user_service)
):
    """
    更新用户资料
    - username: 要更新的用户名
    - request: UserUpdateRequest 包含要更新的用户信息
    - service: UserService 作为依赖注入
    """
    if not username:
        logger.error("用户未登录！")
        return error_response(error=AuthError("用户未登录！"), message="用户未登录！")
    try:
        updated_user = await service.update_user_profile(username, request)
        logger.info(f"用户资料更新成功: {username}")
        return success_response(data=updated_user, message="资料更新成功")
    except UserServiceError as e:
        logger.error(f"用户资料更新失败: {e}")
        return error_response(error=e, message="资料更新失败")
    except Exception as e:
        logger.error(f"用户资料更新过程中发生未知错误: {e}")
        return error_response(e)

@router.post("/password/reset", response_model=APIResponse)
async def change_password(
    username: str = Depends(get_current_username),
    request: PasswordChangeRequest = Body(...),
    service: UserService = Depends(get_user_service)
):
    """
    修改用户密码
    - username: 要更新的用户名
    - request: PasswordChangeRequest 包含旧密码和新密码
    - service: UserService 作为依赖注入
    """
    if not username:
        logger.error("用户未登录！")
        return error_response(message="用户未登录！")
    try:
        result = await service.change_password(username, request)
        logger.info(f"用户密码修改成功: 用户名 {username}")
        
        return success_response(data={"success": result}, message="密码修改成功")
    except UserServiceError as e:
        logger.error(f"用户密码修改失败: {e}")
        return error_response(error=e, message="密码修改失败")
    except Exception as e:
        logger.error(f"用户密码修改过程中发生未知错误: {e}")
        return error_response(e)

@router.post("/delete", response_model=APIResponse)
async def delete_account(
    username: str = Depends(get_current_username),
    service: UserService = Depends(get_user_service)
):
    """
    删除用户账户
    - username: 要删除的用户名
    - service: UserService 作为依赖注入
    """
    if not username:
        logger.error("用户未登录！")
        return error_response(message="用户未登录！")
    try:
        result = await service.delete_user(username)
        logger.info(f"用户账户删除成功: {username}")
        return success_response(data={"success": result}, message="账户删除成功")
    except UserServiceError as e:
        logger.error(f"用户账户删除失败: {e}")
        return error_response(error=e, message="账户删除失败")
    except Exception as e:
        logger.error(f"用户账户删除过程中发生未知错误: {e}")
        return error_response(e)