from typing import Optional, List
from app.models.stock_daily_orm import StockDailyOrm
from app.schemas.stock_daily import StockDailyItem
from app.repositories.stock_daily_repository import StockDailyRepository, StockDailyRepositoryError
from app.external.stock_daily import StockDailyClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
from app.external.exceptions import StockExternalDataError, StockExternalDataProcessingError
from app.schemas.stock_daily import StockDailyResponse, StockDailyResponseItem
from app.repositories.trade_calendar_repository import TradeCalendarRepository
from loguru import logger
from app.utils.stock_utlis import get_stock_exchange_code
from app.core.cache_utlis import redis_cache
from app.models.trade_calendar_orm import TradeCalendarOrm
from app.utils.date_utlis import parse_date

class StockDailyServiceError(Exception):
    """股票日线数据服务异常"""
    pass

class StockDailyService:
    DATE_FORMAT = "%Y%m%d"
    def __init__(self, db_session: AsyncSession,calendar_repository: Optional[TradeCalendarRepository] = None):
        self._repository = StockDailyRepository(db_session)
        self._client = StockDailyClient()
        # 使用传入的交易日历仓储，如果没有则创建一个新的实例
        self._calendar_repository = calendar_repository or TradeCalendarRepository(db_session)

    @redis_cache(ttl=3600)
    async def get_daily_data(self,stock_code: str,start_date: Optional[str] = None,end_date: Optional[str] = None) -> StockDailyResponse:
        """
        获取指定股票代码和日期范围的股票日线数据，并返回 StockDailyResponse 模型。
        如果数据库中没有完整的数据，则从外部接口获取并保存。
        """
        # 获取原始数据
        raw_data = await self._get_raw_daily_data(stock_code, start_date, end_date)
        # 将 ORM 模型转换为 StockDailyResponse 模型 
        daily_data = self._convert_to_response(raw_data)
        return daily_data

    @staticmethod
    def _convert_to_response(stock_data: List[StockDailyOrm]) -> Optional[StockDailyResponse]:
        """将 ORM 数据转换为 StockDailyResponse 格式"""
        if not stock_data:
            return None
        sorted_data = sorted(stock_data, key=lambda x: x.date)
        stock_code = sorted_data[0].stock_code
        # 将 ORM 数据转换为 StockDailyResponseItem
        daily_items = [
            StockDailyResponseItem(
                date=record.date,
                open=record.open,
                high=record.high,
                low=record.low,
                close=record.close,
                change=record.change,
                pct_chg=record.pct_chg,
                vol=record.vol,
                amount=record.amount,
                qfq_factor=record.qfq_factor,
                hfq_factor=record.hfq_factor
            ) for record in sorted_data
        ]
        # 构建 StockDailyResponse
        return StockDailyResponse(
            stock_code=stock_code,
            daily=daily_items,
            data_count=len(daily_items),
            start_date=sorted_data[0].date,
            end_date=sorted_data[-1].date
        )
    
    async def _get_raw_daily_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[StockDailyOrm]:
        """
        获取指定股票代码和日期范围的股票日线数据。
        如果数据库中没有完整的数据，则从外部接口获取并保存。
        """
        try:
            # 查询数据库中的数据
            existing_records = await self._repository.find_stock_daily(stock_code, start_date, end_date)
            logger.info(f"查询数据库中的数据，股票代码: {stock_code}, 起始日期: {start_date}, 结束日期: {end_date}, 数据条数: {len(existing_records)}")
            # 如果数据不存在或有缺失，从外部接口获取并保存该股票从入市至今的数据
            if not existing_records or await self._has_missing_dates(existing_records, start_date, end_date):
                logger.info(f"数据库中没有完整的数据，开始从外部接口获取数据，股票代码: {stock_code}, 起始日期: {start_date}, 结束日期: {end_date}")
                # 从外部接口获取数据
                stock_daily_items = await StockDailyClient.get_daily_items(stock_code)
                
                if not stock_daily_items:
                    return []

                # 将 Pydantic 模型转换为 ORM 模型
                orm_items = StockDailyService._daily_to_orm(stock_daily_items)

                # 保存到数据库
                await self._repository.save_stock_daily(orm_items)

                # 重新查询数据库以获取完整数据
                existing_records = await self._repository.find_stock_daily(stock_code, start_date, end_date)
                return existing_records
            else:
                logger.info(f"数据库中已有完整的数据，直接返回数据，股票代码: {stock_code}, 起始日期: {start_date}, 结束日期: {end_date}")  
                return existing_records
        except StockDailyRepositoryError as e:
            logger.error(f"数据交互时候出现错误: {e}")
            raise StockDailyServiceError(f"数据交互时候出现错误，股票代码: {stock_code}, 错误: {e}") from e
        except StockExternalDataError as e:
            logger.error(f"外部数据获取失败: {e}")
            raise StockDailyServiceError(f"外部数据获取失败，股票代码: {stock_code}, 错误: {e}") from e
        except StockExternalDataProcessingError as e:
            logger.error(f"外部数据处理失败: {e}")
            raise StockDailyServiceError(f"外部数据处理失败，股票代码: {stock_code}, 错误: {e}") from e
        except StockDailyServiceError as e:
            raise e
        except Exception as e:
            logger.error(f"服务内部出现未知错误: {e}")
            raise StockDailyServiceError(f"服务内部出现未知错误，股票代码: {stock_code}, 错误: {e}") from e
    
    @redis_cache(ttl=3600)
    async def _get_full_trade_calendar(self,exchange_code: str) -> list[TradeCalendarOrm]:
        """
        获取并缓存某个交易所的完整交易日历（不限制日期范围）

        Args:
            exchange_code (str): 交易所代码，如 SZ、SH
        Returns:
            list[TradeCalendarOrm]: 交易日历列表
        """
        calendar_items = await self._calendar_repository.find_trade_calendar(exchange_code=exchange_code)
        
        return calendar_items
        
    async def _has_missing_dates(
        self,
        stock_daily_records: List[StockDailyOrm],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> bool:
        """
        检查指定时间范围内的日线数据是否有缺失日期

        Args:
            stock_daily_records (List[StockDailyOrm]): 数据库中已有的日线记录
            start_date (Optional[date]): 起始日期，如果为None则使用记录中最早的日期
            end_date (Optional[date]): 结束日期，如果为None则使用今天的日期

        Returns:
            bool: 是否有缺失日期，True表示有缺失，False表示数据完整
        """
        try:
            if not stock_daily_records:
                logger.warning("未找到任何日线记录，数据不完整")
                return False
            stock_code= stock_daily_records[0].stock_code
            exchange_code=get_stock_exchange_code(stock_code)
            # 设置日期范围
            sorted_records = sorted(stock_daily_records, key=lambda x: x.date)
            actual_start_date = parse_date(start_date) or sorted_records[0].date
            actual_end_date = parse_date(end_date) or datetime.now()
            # 从交易日历仓储获取应有的交易日
            calendar_items = await self._get_full_trade_calendar(exchange_code=exchange_code)
            trade_dates_required = {
                item.trade_date for item in calendar_items
                if actual_start_date <= item.trade_date <= actual_end_date
            }
            logger.debug(f"区间 {actual_start_date} 至 {actual_end_date} 应有交易日数量: {len(trade_dates_required)}")

            # 获取已有日线数据的日期
            record_dates = {record.date for record in stock_daily_records}
            logger.debug(f"已有日线记录日期数: {len(record_dates)}")

            # 判断是否覆盖所有交易日
            missing_dates = trade_dates_required - record_dates
            if missing_dates:
                logger.warning(f"存在缺失的交易日: {sorted(missing_dates)}")
                return True
            else:
                logger.info(f"所有交易日均已覆盖，股票代码: {stock_code}, 起始日期: {actual_start_date}, 结束日期: {actual_end_date}")
                return False
        except Exception as e:
            logger.error(f"检查日线数据完整性时出错: {e}")
            raise StockDailyServiceError(f"检查数据完整性失败: {e}") from e

    
    @staticmethod
    def _daily_to_orm(daily_items: list[StockDailyItem]) -> list[StockDailyOrm]:
        """
        将 Pydantic 模型列表转换为 ORM 模型列表
        """
        try:
            return [daily_item.to_orm() for daily_item in daily_items]
        except Exception as e:
            logger.error(f"转换数据模型时发生错误: {e}")
            raise StockDailyServiceError(f"转换数据模型时发生错误: {e}") from e
    
    @classmethod
    def _parse_date(cls, date_str: Optional[str]) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, cls.DATE_FORMAT).date()
        except ValueError as e:
            logger.error(f"日期格式错误: {date_str}，应为YYYYMMDD格式")
            raise StockDailyServiceError(f"日期格式错误: {date_str}，应为YYYYMMDD格式") from e
        
    @staticmethod
    def _convert_decimal(value):
        try:
            if isinstance(value, Decimal):
                return float(value)  
            return value
        except Exception as e:
            logger.error(f"转换数据时发生错误: {e}")
            raise StockDailyServiceError(f"转换数据时发生错误: {e}") from e

if __name__ == "__main__":
    import asyncio
    from app.core.database import get_async_db
    from fastapi.responses import JSONResponse
    async def test_get_raw_daily_data():
        """测试获取股票日线数据"""
        try:
            async for db in get_async_db():

                service = StockDailyService(db)
                stock_code = "000001"
                start_date = "20220101"
                end_date = "20221001"
                stock_data = await service._get_raw_daily_data(stock_code, start_date, end_date)
                logger.info(f"已找到股票代码为{stock_code}的 {len(stock_data)} 条数据")
                for record in stock_data:
                    logger.info(record)
                break
        except Exception as e:
            logger.error(f"获取股票数据时发生错误: {e}")
    async def test_get_daily_data():
        """测试获取股票日线数据"""
        try:
            async for db in get_async_db():
                service = StockDailyService(db)
                stock_code = "300059"
                start_date = "20220101"
                end_date = "20220110"
                daily_data = await service.get_daily_data(stock_code, start_date, end_date)
                (f"已找到股票代码为{stock_code}的日线数据")
                logger.info(daily_data)
                logger.info(JSONResponse(content=daily_data.model_dump(mode="json")).body.decode("utf-8"))
                break
        except Exception as e:
            logger.error(f"获取股票日线时发生错误: {e}")
    async def main():
        """运行测试"""
        try:
            await test_get_raw_daily_data()
            await test_get_daily_data()
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()

    asyncio.run(main())