from fastapi import Depends
from app.core.token_utils import oauth2_scheme,decode_access_token
from loguru import logger
from typing import Optional


async def get_current_username(token: str = Depends(oauth2_scheme)) -> Optional[str]:
    """
    解析 token，返回 username。 
    如果 token 无效或解析失败，直接抛出 HTTPException 异常。
    """
    try:
        # 解码 token，获取 payload 数据
        payload = decode_access_token(token)
        # 从 payload 中获取用户名
        username = payload.get("sub")
        return username  # 如果解析成功，返回用户名
    except Exception as e:
        logger.error(f"Token 解析失败: {e}")
        return None
    
async def is_user_authenticated(token: str = Depends(oauth2_scheme)) -> bool:
    """
    解析 token，成功返回 True，失败返回 False
    """
    try:
        # 解码 token，获取 payload 数据
        payload = decode_access_token(token)
        # 从 payload 中获取用户名
        username = payload.get("sub")
        return True  # 如果解析成功，返回True
    except Exception as e:
        logger.error(f"Token 解析失败: {e}")
        return False