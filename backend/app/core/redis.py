import redis.asyncio as aioredis
from app.config.redis import redis_settings

# 统一 Redis 连接 URL
REDIS_URL = redis_settings.redis_url

# 创建 Redis 客户端，适配二进制数据
redis_client = aioredis.Redis.from_url(
    REDIS_URL,
    decode_responses=False
)

async def set_cache(key: str, value: bytes, ttl: int = 3600) -> bool:
    """
    设置缓存（适合存储序列化后的对象）
    :param key: 缓存键
    :param value: 缓存值（应为 bytes）
    :param ttl: 过期时间（秒）
    :return: 是否设置成功
    """
    return await redis_client.setex(key, ttl, value)

async def get_cache(key: str) -> bytes | None:
    """
    获取缓存
    :param key: 缓存键
    :return: 缓存值（bytes）
    """
    return await redis_client.get(key)

async def delete_cache(key: str) -> bool:
    """
    删除指定缓存键
    :param key: 缓存键
    :return: 是否成功删除
    """
    result = await redis_client.delete(key)
    return result == 1

async def clear_all_cache() -> bool:
    """
    清除 Redis 中所有键（慎用！）
    :return: 是否成功清除
    """
    await redis_client.flushdb()
    return True
