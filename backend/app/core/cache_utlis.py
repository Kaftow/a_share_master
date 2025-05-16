import functools
import pickle
import hashlib
import json
from typing import Callable, Any, Awaitable
from app.core.redis import get_cache, set_cache
from loguru import logger

def _make_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """
    为函数生成唯一缓存键，支持实例方法和静态方法
    """
    # 忽略第一个参数（self 或 cls）
    if args and hasattr(args[0], '__class__'):
        args_to_serialize = args[1:]
    else:
        args_to_serialize = args

    try:
        raw = pickle.dumps((args_to_serialize, kwargs))
    except Exception:
        raw = str((args_to_serialize, kwargs)).encode()

    hash_digest = hashlib.sha256(raw).hexdigest()
    return f"cache:{func.__module__}.{func.__name__}:{hash_digest}"

def redis_cache(ttl: int = 3600):
    """
    装饰器：缓存异步函数返回值
    :param ttl: 缓存有效期（秒）
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = _make_cache_key(func, args, kwargs)
            cached = await get_cache(cache_key)
            if cached:
                logger.info(f"缓存命中: {cache_key}")
                try:
                    return pickle.loads(cached)
                except Exception:
                    pass  # 缓存损坏时跳过
            try:
                result = await func(*args, **kwargs)
                await set_cache(cache_key, pickle.dumps(result), ttl)  # 只有成功执行才缓存
                logger.info(f"缓存设置成功: {cache_key}")
                return result
            except Exception as e:
                logger.error(f"函数执行出错，缓存不会更新: {e}")
                raise  # 抛出异常，确保不缓存错误结果
        return wrapper
    return decorator
