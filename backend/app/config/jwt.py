from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION: int

    class Config:
        env_file = ".env.jwt"

# 实例化配置对象
jwt_settings = JWTSettings()