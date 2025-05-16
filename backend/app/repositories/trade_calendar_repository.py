from app.models.trade_calendar_orm import TradeCalendarOrm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from loguru import logger
from sqlalchemy import desc
from typing import Optional

class TradeCalendarRepositoryError(Exception):
    """用于处理交易日历数据存取过程中出现的异常"""
    pass

class TradeCalendarRepository:
    """
    交易日历数据仓库
    """
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save_trade_calendar(self, orm_items: list[TradeCalendarOrm]) -> None:
        try:
            for orm_item in orm_items:
                await self._db.merge(orm_item)  # 批量保存或更新交易日历数据
            await self._db.commit()
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"保存交易日历数据时发生错误: {e}")
            raise TradeCalendarRepositoryError("保存交易日历数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"保存交易日历数据时发生未知错误: {e}")
            raise TradeCalendarRepositoryError("保存交易日历数据时发生未知错误", e)

    async def find_trade_calendar(
        self, 
        exchange_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[TradeCalendarOrm]:
        """
        查询交易日历数据，支持日期范围过滤

        Args:
            exchange_code (str): 交易所代码
            start_date (Optional[date], optional): 开始日期. Defaults to None.
            end_date (Optional[date], optional): 结束日期. Defaults to None.

        Returns:
            list[TradeCalendarOrm]: 交易日历记录列表

        Raises:
            TradeCalendarRepositoryError: 数据库操作异常
        """
        
        try:
            # 构建基础查询
            stmt = select(TradeCalendarOrm).where(
                TradeCalendarOrm.exchange_code == exchange_code
            )
            # 添加日期范围过滤条件
            if start_date:
                stmt = stmt.where(TradeCalendarOrm.trade_date >= start_date)
            if end_date:
                stmt = stmt.where(TradeCalendarOrm.trade_date <= end_date)
            # 按日期排序
            stmt = stmt.order_by(TradeCalendarOrm.trade_date)
            result = await self._db.execute(stmt)
            return result.scalars().all()  # 返回该交易所所有的交易日历记录
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"查询交易日历数据时发生错误: {e}")
            raise TradeCalendarRepositoryError("查询交易日历数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"查询交易日历数据时发生未知错误: {e}")
            raise TradeCalendarRepositoryError("查询交易日历数据时发生未知错误", e)
        
    async def get_latest_trade_day(self, exchange_code: str) -> TradeCalendarOrm:
        """
        获取指定交易所的最近交易日
        :param exchange_code: 交易所代码，如SH（上交所）、SZ（深交所）、BJ（北交所）
        :return: 返回最近交易日的交易日历记录
        """
        try:
            # 查询指定交易所的所有交易日历，并按照交易日期降序排列
            stmt = select(TradeCalendarOrm).where(
                TradeCalendarOrm.exchange_code == exchange_code
            ).order_by(desc(TradeCalendarOrm.trade_date))

            result = await self._db.execute(stmt)
            latest_trade_day = result.scalars().first()  # 获取最早的交易日（即最近的交易日）

            return latest_trade_day
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"查询最近交易日数据时发生错误: {e}")
            raise TradeCalendarRepositoryError("查询最近交易日数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"查询最近交易日数据时发生未知错误: {e}")
            raise TradeCalendarRepositoryError("查询最近交易日数据时发生未知错误", e)

if __name__ == "__main__":
    from app.core.database import get_async_db
    from app.external.trade_calendar import TradeCalendarClient
    import asyncio

    async def test_save_trade_calendar():
        """测试保存交易日历数据"""
        try:
            # 从外部获取数据
            client = TradeCalendarClient()
            trade_calendar_item = await client.get_exchange_trade_calendar_item("SH")
            trade_calendar_orms = trade_calendar_item.to_orm()

            async for db in get_async_db():
                repository = TradeCalendarRepository(db)
                await repository.save_trade_calendar(trade_calendar_orms)
                logger.info("交易日历数据保存成功")
        except Exception as e:
            logger.error(f"测试保存交易日历数据时发生错误: {e}")

    async def test_find_trade_calendar():
        """测试查询交易日历数据"""
        try:
            async for db in get_async_db():
                repository = TradeCalendarRepository(db)

                exchange_code = "SH"
                start_date = date(2023, 1, 1)
                end_date = date(2023, 12, 31)
                records = await repository.find_trade_calendar(exchange_code=exchange_code,start_date=start_date,end_date=end_date)
                logger.info(f"找到 {exchange_code} 交易所的 {len(records)} 条交易日历数据")
                for record in records:
                    logger.info(record)
                break
        except Exception as e:
            logger.error(f"测试查询交易日历数据时发生错误: {e}")

    async def test_get_latest_trade_day():
        """测试获取最近交易日"""
        try:
            async for db in get_async_db():
                repository = TradeCalendarRepository(db)
                exchange_code = "SH"
                latest_trade_day = await repository.get_latest_trade_day(exchange_code=exchange_code)
                if latest_trade_day:
                    logger.info(f"最近交易日：{latest_trade_day}")
                else:
                    logger.info(f"未找到 {exchange_code} 交易所的最近交易日")
        except Exception as e:
            logger.error(f"测试获取最近交易日时发生错误: {e}")

    async def main():
        """运行所有测试"""
        try:
            await test_save_trade_calendar()
            await test_find_trade_calendar()
            await test_get_latest_trade_day()
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()

    asyncio.run(main())
