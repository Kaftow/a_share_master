from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.trade_calendar_service import TradeCalendarService
from app.core.database import get_async_db
from loguru import logger
from datetime import datetime

apscheduler = AsyncIOScheduler()

async def update_trade_calendar_task():
    """定时更新交易日历的任务"""
    try:
        async for session in get_async_db():
            service = TradeCalendarService(session)
            await service.refresh_all_exchange_calendars()
        logger.info("交易日历定时检查完成")
    except Exception as e:
        logger.error(f"交易日历定时任务执行失败: {e}")

def start_scheduler():
    """初始化并启动调度器"""
    # 添加定时任务，并设置立即执行
    apscheduler.add_job(
        update_trade_calendar_task,
        trigger=IntervalTrigger(hours=12),
        id="update_trade_calendar",
        replace_existing=True,
        next_run_time=datetime.now()  # 设置立即执行
    )
    apscheduler.start()
    logger.info("调度器启动完成")


def stop_scheduler():
    """关闭调度器"""
    apscheduler.shutdown()
    logger.info("调度器已关闭")
