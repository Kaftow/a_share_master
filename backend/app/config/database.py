from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class DatabaseSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def db_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def async_db_url(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        env_file = ".env.db"

# 实例化配置对象
database_settings = DatabaseSettings()
