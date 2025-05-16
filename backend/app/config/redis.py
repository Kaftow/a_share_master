from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env.redis"

# 实例化配置对象
redis_settings = RedisSettings()

