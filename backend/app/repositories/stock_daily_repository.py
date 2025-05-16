from app.models.stock_daily_orm import StockDailyOrm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from loguru import logger

class StockDailyRepositoryError(Exception):
    """用于处理股票日线数据存取过程中出现的异常"""
    pass

class StockDailyRepository:
    """
    股票日线数据仓库
    """
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save_stock_daily(self, orm_items: list[StockDailyOrm])-> None:
        try:
            for orm_item in orm_items:
                await self._db.merge(orm_item)
            await self._db.commit()
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"保存股票日线数据时发生错误: {e}")
            raise StockDailyRepositoryError("保存股票日线数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"保存股票日线数据时发生未知错误: {e}")
            raise StockDailyRepositoryError("保存股票日线数据时发生未知错误", e)

    async def find_stock_daily(self, stock_code: str,start_date: Optional[date]=None, end_date: Optional[date]=None)-> list[StockDailyOrm]:
        try:
            stmt = select(StockDailyOrm).where(StockDailyOrm.stock_code == stock_code)
            if start_date:
                stmt = stmt.where(StockDailyOrm.date >= start_date)
            if end_date:
                stmt = stmt.where(StockDailyOrm.date <= end_date)
            stmt = stmt.order_by(StockDailyOrm.date)
            result = await self._db.execute(stmt)
            stock_daily = result.scalars().all()
            return stock_daily
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"查询股票日线数据时发生错误: {e}")
            raise StockDailyRepositoryError("查询股票日线数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"查询股票日线数据时发生未知错误: {e}")
            raise StockDailyRepositoryError("查询股票日线数据时发生未知错误", e)

if __name__ == "__main__":
    from app.core.database import get_async_db
    import asyncio
    async def test_save_stock_daily():
        """测试保存股票日线数据"""
        try:
            from app.external.stock_daily import StockDailyClient
            client= StockDailyClient()
            stock_code = "000001"
            start_date = "20230101"
            end_date = "20231001"
            stock_daily_items = await client.get_daily_items(stock_code, start_date, end_date)
            stock_daily_orms = [item.to_orm() for item in stock_daily_items]
    
            async for db in get_async_db():
                repository = StockDailyRepository(db)
                await repository.save_stock_daily(stock_daily_orms)
                logger.info("股票日线数据保存成功")

        except Exception as e:
            logger.error(f"测试保存股票日线模块时发生错误: {e}")
    async def test_find_stock_daily():
        """测试查询股票日线数据"""
        try:
            async for db in get_async_db():
                repository = StockDailyRepository(db)

                stock_code = "000001"
                start_date = date(2023, 1, 1)
                end_date = date(2023, 10, 1)

                records = await repository.find_stock_daily(
                    stock_code=stock_code,
                    start_date=start_date,
                    end_date=end_date
                )
                logger.info(f"找到股票代码为{stock_code}的 {len(records)} 条数据")
                for record in records:
                    logger.info(record)

        except Exception as e:
            logger.error(f"测试查询股票日线模块时发生错误: {e}")
    async def main():
        """运行所有测试"""
        try:
            await test_save_stock_daily()
            await test_find_stock_daily()
        finally:
            # 关闭数据库连接
            from app.core.database import async_engine
            await async_engine.dispose()
    # 执行测试
    asyncio.run(main())
