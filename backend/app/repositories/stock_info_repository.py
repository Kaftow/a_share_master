from app.models.stock_info_orm import StockInfoOrm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from loguru import logger

class StockInfoRepositoryError(Exception):
    """用于处理个股信息数据存取过程中出现的异常"""
    pass

class StockInfoRepository:
    """
    个股信息数据仓库
    """
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save_stock_info(self, orm_item: StockInfoOrm)-> None:
        try:
            await self._db.merge(orm_item)
            await self._db.commit()
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"保存个股信息数据时发生错误: {e}")
            raise StockInfoRepositoryError("保存个股信息数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"保存个股信息数据时发生未知错误: {e}")
            raise StockInfoRepositoryError("保存个股信息数据时发生未知错误", e)

    async def find_stock_info(self, stock_code: str)-> Optional[StockInfoOrm]:
        try:
            stmt = select(StockInfoOrm).where(StockInfoOrm.stock_code == stock_code)
            result = await self._db.execute(stmt)
            stock_info = result.scalars().first()
            return stock_info
        except SQLAlchemyError as e:
            await self._db.rollback()
            logger.error(f"查询个股信息数据时发生错误: {e}")
            raise StockInfoRepositoryError("查询个股信息数据时数据库操作失败", e)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"查询个股信息数据时发生未知错误: {e}")
            raise StockInfoRepositoryError("查询个股信息数据时发生未知错误", e)

if __name__ == "__main__":
    from app.core.database import get_async_db
    import asyncio
    async def test_save_stock_info():
        """测试保存个股信息数据"""
        try:
            from app.external.stock_info import StockInfoClient
            client= StockInfoClient()
            stock_code = "000001"
            stock_info_item = await client.get_info_item(stock_code)
            stock_info_orm = stock_info_item.to_orm()
    
            async for db in get_async_db():
                repository = StockInfoRepository(db)
                await repository.save_stock_info(stock_info_orm)
                logger.info("个股信息数据保存成功")

        except Exception as e:
            logger.error(f"测试保存个股信息模块时发生错误: {e}")

    async def test_find_stock_info():
        """测试查询个股信息数据"""
        try:
            async for db in get_async_db():
                repository = StockInfoRepository(db)

                stock_code = "000001"

                record = await repository.find_stock_info(
                    stock_code=stock_code
                )
                if record:
                    logger.info(f"已找到{stock_code}的个股数据")
                    logger.info(record)
                else:
                    logger.info(f"No stock info found for {stock_code}")

        except Exception as e:
            logger.error(f"测试查询个股信息模块时发生错误: {e}")
    async def main():
        """运行所有测试"""
        try:
            await test_save_stock_info()
            await test_find_stock_info()
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()
    asyncio.run(main())