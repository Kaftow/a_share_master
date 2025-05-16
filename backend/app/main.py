from fastapi import FastAPI, APIRouter
from app.models.stock_daily_orm import Base
from app.core.database import engine
from app.api import stock_router,trade_calendar_router, user_router
from loguru import logger
from app.core.apscheduler import apscheduler
api_prefix = "/api/v1"

app = FastAPI(title="A股大王", docs_url=f"{api_prefix}/docs", redoc_url=f"{api_prefix}/redoc")
Base.metadata.create_all(bind=engine) 
logger.info("数据库表结构创建成功")

api_v1_router = APIRouter()

# 将所有子路由模块包含到统一的API路由器中
api_v1_router.include_router(stock_router.router)
api_v1_router.include_router(trade_calendar_router.router)
api_v1_router.include_router(user_router.router)

# 统一设置前缀为 /api/v1
app.include_router(api_v1_router, prefix=api_prefix)
apscheduler.start()

