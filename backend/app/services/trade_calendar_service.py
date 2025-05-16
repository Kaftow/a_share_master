from typing import Optional, List
from datetime import date
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.trade_calendar_repository import TradeCalendarRepository, TradeCalendarRepositoryError
from app.schemas.trade_calendar import TradeCalendarResponse, TradeCalendarItem,ExchangeLastTradingDayItem,ExchangeLastTradingDayResponse
from app.external.trade_calendar import TradeCalendarClient
from app.external.exceptions import StockExternalDataError, StockExternalDataProcessingError
from datetime import timedelta,datetime
from app.models.trade_calendar_orm import TradeCalendarOrm
from app.core.cache_utlis import redis_cache

EXCHANGE_CODES = ["SH", "SZ", "BJ"]

class TradeCalendarServiceError(Exception):
    """交易日历服务异常"""
    pass

class TradeCalendarService:
    
    def __init__(self, db_session: AsyncSession):
        self._repository = TradeCalendarRepository(db_session)
        self._client = TradeCalendarClient()

    @redis_cache(ttl=3600)
    async def get_trade_calendar_data(self,exchange_code: str,start_date: Optional[date] = None,end_date: Optional[date] = None) -> TradeCalendarResponse:
        """
        获取指定交易所的交易日历数据，并返回标准响应格式
        """
        try:
            # 获取原始数据
            raw_data = await self.get_raw_trade_calendar(exchange_code, start_date, end_date)
            # 转换为响应格式
            return self._convert_calendar_to_response(raw_data)
        except Exception as e:
            logger.error(f"获取交易日历响应数据时发生错误: {e}")
            raise TradeCalendarServiceError(f"获取交易日历响应数据失败: {e}")

    @redis_cache(ttl=3600)
    async def get_latest_trading_day_data(
        self,
        exchange_code: str
    ) -> ExchangeLastTradingDayResponse:
        """
        获取指定交易所的最新交易日，并返回标准响应格式
        """
        try:
            # 获取原始数据
            raw_data = await self.get_raw_latest_trading_day(exchange_code)
            # 转换为响应格式
            return self._convert_last_trading_day_to_response(raw_data)
        except Exception as e:
            logger.error(f"获取最新交易日响应数据时发生错误: {e}")
            raise TradeCalendarServiceError(f"获取最新交易日响应数据失败: {e}")

    async def _fetch_and_save_calendar(self, exchange_code: str, start_date: Optional[date]=None,end_date:Optional[date]=None) -> None:
        """
        从外部接口获取交易日历数据并保存到数据库
        start_date (date, optional): 起始日期（可选），如果不传，默认为开市日期
        end_date (date, optional): 结束日期（可选），如果不传，默认为今天
        Args:
            exchange_code (str): 交易所代码
            
        Raises:
            StockExternalDataError: 获取外部数据失败时抛出
            TradeCalendarRepositoryError: 保存数据失败时抛出
        """
        logger.info(f"正在从外部接口获取{exchange_code}交易所的数据")
        try:
            # 从外部接口获取交易日历数据
            calendar_item = await self._client.get_exchange_trade_calendar_item(exchange_code=exchange_code,start_date=start_date,end_date=end_date)
            if calendar_item:
                # 转换为ORM对象并保存到数据库
                orm_items = calendar_item.to_orm()
                if orm_items:
                    await self._repository.save_trade_calendar(orm_items)
                    logger.info(f"成功保存{exchange_code}交易所的{len(orm_items)}条交易日历数据")
                else:
                    logger.error(f"{exchange_code}交易所接口返回的数据无法转换为ORM对象")
                    raise StockExternalDataProcessingError(f"{exchange_code}交易所接口数据无效")
            else:
                logger.error(f"获取{exchange_code}交易所的交易日历数据失败")
                raise StockExternalDataError(f"获取{exchange_code}交易所的交易日历数据失败")
        except StockExternalDataError as e:
            logger.error(f"获取外部数据失败: {e}")
            raise TradeCalendarServiceError(f"获取外部数据失败: {e}")
        except TradeCalendarRepositoryError as e:
            logger.error(f"保存数据库时发生错误: {e}")
            raise e  # 重新抛出保存数据错误
        except Exception as e:
            logger.error(f"增量获取并保存{exchange_code}交易日历时发生未知错误: {e}")
            raise TradeCalendarServiceError(f"增量获取并保存{exchange_code}交易日历失败: {e}")

    async def get_raw_trade_calendar(
        self,
        exchange_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TradeCalendarOrm]:
        """
        获取指定交易所的交易日历数据
        如果数据库中没有数据，则从外部接口获取并保存
        """
        try:
            # 从数据库获取交易日历数据
            trade_dates = await self._repository.find_trade_calendar(exchange_code,start_date,end_date)
            
            if not trade_dates:
                # 如果数据库中没有数据，从外部接口获取
                logger.info(f"数据库中没有{exchange_code}交易所的数据，从外部接口获取")
                await self._fetch_and_save_calendar(exchange_code)
                # 重新从数据库获取数据
                trade_dates = await self._repository.find_trade_calendar(exchange_code,start_date,end_date)
            # 转换为响应格式
            return trade_dates

        except TradeCalendarRepositoryError as e:
            logger.error(f"数据库操作失败: {e}")
            raise TradeCalendarServiceError(f"获取交易日历数据失败: {e}")
        except StockExternalDataError as e:
            logger.error(f"获取外部数据失败: {e}")
            raise TradeCalendarServiceError(f"获取外部交易日历数据失败: {e}")
        except Exception as e:
            logger.error(f"处理交易日历数据时发生未知错误: {e}")
            raise TradeCalendarServiceError(f"处理交易日历数据时发生未知错误: {e}")

    async def get_raw_latest_trading_day(self, exchange_code: str) -> TradeCalendarOrm:
        """获取指定交易所的最新交易日"""
        try:
            latest_day = await self._repository.get_latest_trade_day(exchange_code)
            if not latest_day:
                raise TradeCalendarRepositoryError(f"未找到{exchange_code}的最新交易日数据")
            return latest_day
        except TradeCalendarRepositoryError as e:
            logger.error(f"获取最新交易日失败: {e}")
            raise TradeCalendarServiceError(f"获取最新交易日失败: {e}")
        except Exception as e:
            logger.error(f"获取最新交易日时发生未知错误: {e}")
            raise TradeCalendarServiceError(f"获取最新交易日时发生未知错误: {e}")
        
    @staticmethod
    def _convert_calendar_to_response(
        calendar_data: List[TradeCalendarOrm],
    ) -> TradeCalendarResponse:
        """将数据库记录转换为响应格式"""
        try:
            if not calendar_data:
                logger.error("将数据库记录转换为响应格式失败，没有找到交易日历数据！")
                raise TradeCalendarServiceError("将数据库记录转换为响应格式失败，没有找到交易日历数据！")
            else:
                exchange_code=calendar_data[0].exchange_code
                trade_dates = sorted([item.trade_date for item in calendar_data])
                return TradeCalendarResponse(
                    exchange_code=exchange_code,
                    trade_dates=trade_dates,
                    total_count = len(trade_dates),
                    first_trade_date = trade_dates[0],
                    last_trade_date = trade_dates[-1],
                )
        except TradeCalendarServiceError as e:
            logger.error(f"转换交易日历数据时发生错误: {e}")
            raise e
        except Exception as e:
            logger.error(f"转换交易日历数据时发生未知错误: {e}")
            raise TradeCalendarServiceError(f"转换交易日历数据时发生未知错误: {e}")
        
    @staticmethod
    def _convert_last_trading_day_to_response(
        last_trading_day_data: TradeCalendarOrm,
    ) -> ExchangeLastTradingDayResponse:
        """将数据库记录转换为响应格式"""
        try:
            if not last_trading_day_data:
                logger.error("将数据库记录转换为响应格式失败，没有找到最新交易日数据！")
                raise Exception("将数据库记录转换为响应格式失败，没有找到最新交易日数据！")
            else:
                return ExchangeLastTradingDayResponse(
                    exchange_code=last_trading_day_data.exchange_code,
                    last_trading_day=last_trading_day_data.trade_date
                )
        except Exception as e:
            logger.error(f"转换最新交易日数据时发生错误: {e}")
            raise TradeCalendarServiceError(f"转换最新交易日数据失败: {e}")
    
    async def refresh_trade_calendar(self, exchange_code: str) -> None:
        """
        检查并更新交易日历数据
        定期检查最新交易日，如果发现数据不是最新的则更新
        """
        try:
            # 获取数据库中的最新交易日
            db_latest_day_item=await self._repository.get_latest_trade_day(exchange_code)
            if not db_latest_day_item:
                logger.warning(f"数据库中没有{exchange_code}的交易日历数据，将进行全量更新")
                await self.get_raw_trade_calendar(exchange_code)
                return
            db_latest_day = db_latest_day_item.trade_date
            # 从外部接口获取最新交易日
            external_latest_day_item= await self._client.get_exchange_last_trading_day_item(exchange_code)
            if not external_latest_day_item:
                logger.error("无法从外部接口获取最新交易日信息")
                return
            external_latest_day = external_latest_day_item.last_trading_day
            if not external_latest_day:
                logger.error("无法从外部接口获取最新交易日信息")
                return
            # 比较日期是否一致
            if external_latest_day > db_latest_day:
                logger.info(f"发现新的交易日数据，从{db_latest_day}更新到{external_latest_day}")
                # 更新交易日历数据
                await self._fetch_and_save_calendar(exchange_code,start_date=db_latest_day + timedelta(days=1), end_date=external_latest_day)
            else:
                logger.info(f"{exchange_code}的交易日历数据是最新的，最新交易日为{db_latest_day}")
        except TradeCalendarRepositoryError as e:
            logger.error(f"获取数据库中交易日历时发生错误: {e}")
            raise TradeCalendarServiceError(f"检查和更新交易日历失败: {e}")
        except Exception as e:
            logger.error(f"检查和更新交易日历时发生错误: {e}")
            raise TradeCalendarServiceError(f"检查和更新交易日历失败: {e}")
        
    async def refresh_all_exchange_calendars(self) -> None:
        """
        检查并更新所有交易所的交易日历数据
        """
        try:
            for exchange_code in EXCHANGE_CODES:
                await self.refresh_trade_calendar(exchange_code)
        except TradeCalendarServiceError as e:
            raise e
        except Exception as e:
            logger.error(f"更新所有交易所的交易日历数据时出现未知错误: {e}")
            raise TradeCalendarServiceError(f"更新所有交易所的交易日历数据时出现未知错误: {e}")

if __name__ == "__main__":
    import asyncio
    from app.core.database import get_async_db
    
    async def test_get_raw_trade_calendar():
        """测试获取交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                calendar = await service.get_raw_trade_calendar("SH")
                if calendar and calendar:
                    total = len(calendar)
                    head = calendar[:5]  # 前5个交易日
                    tail = calendar[-5:]  # 后5个交易日
                    logger.info(f"获取到指定日期范围的交易日历数据 (共{total}个交易日):")
                    logger.info(f"前5个交易日: {head}")
                    logger.info(f"后5个交易日: {tail}")
                else:
                    logger.warning("未获取到交易日历数据")
                break
        except Exception as e:
            logger.error(f"测试获取交易日历时发生错误: {e}")

    async def test_get_raw_latest_trading_day():
        """测试获取最新交易日"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                latest_day = await service.get_raw_latest_trading_day("SH")
                logger.info(f"获取到最新交易日：{latest_day}")
                break
        except Exception as e:
            logger.error(f"测试获取最新交易日时发生错误: {e}")

    async def test_fetch_and_save_calendar():
        """测试获取并保存交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                await service._fetch_and_save_calendar("SH")
                logger.info("完成交易日历数据获取和保存")
                break
        except Exception as e:
            logger.error(f"测试获取并保存交易日历时发生错误: {e}")

    async def test_get_raw_trade_calendar_with_date_range():
        """测试获取指定日期范围的交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                start_date = date(2023, 1, 1)
                end_date = date(2023, 12, 31)
                calendar = await service.get_raw_trade_calendar("SH", start_date, end_date)
                if calendar:
                    total = len(calendar)
                    head = calendar[:5]  # 前5个交易日
                    tail = calendar[-5:]  # 后5个交易日
                    logger.info(f"获取到交易日历数据 (共{total}个交易日):")
                    logger.info(f"时间范围: {start_date} 至 {end_date}")
                    logger.info(f"前5个交易日: {head}")
                    logger.info(f"后5个交易日: {tail}")
                else:
                    logger.warning("未获取到交易日历数据")
                break
        except Exception as e:
            logger.error(f"测试获取指定日期范围的交易日历时发生错误: {e}")

    async def test_check_and_update_calendar():
        """测试检查和更新交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                await service.refresh_trade_calendar("SH")
                logger.info("完成交易日历检查和更新")
                break
        except Exception as e:
            logger.error(f"测试检查和更新交易日历时发生错误: {e}")

    async def test_get_trade_calendar_data():
        """测试获取交易日历响应数据"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                start_date = date(2023, 1, 1)
                end_date = date(2023, 12, 31)
                response = await service.get_trade_calendar_data("SH", start_date, end_date)
                logger.info("获取到交易日历响应数据:")
                logger.info(f"交易所: {response.exchange_code}")
                logger.info(f"总交易日数: {response.total_count}")
                logger.info(f"开始日期: {response.first_trade_date}")
                logger.info(f"结束日期: {response.last_trade_date}")
                break
        except Exception as e:
            logger.error(f"测试获取交易日历响应数据时发生错误: {e}")

    async def test_get_latest_trading_day_data():
        """测试获取最新交易日响应数据"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                response = await service.get_latest_trading_day_data("SH")
                logger.info(f"获取到最新交易日响应数据: {response}")
                logger.info(f"交易所: {response.exchange_code}")
                logger.info(f"最新交易日: {response.last_trading_day}")
                break
        except Exception as e:
            logger.error(f"测试获取最新交易日响应数据时发生错误: {e}")

    async def test_refresh_trade_calendar():
        """测试刷新单个交易所的交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                await service.refresh_trade_calendar("SH")
                logger.info("刷新交易所 SH 的交易日历完成")
                break
        except Exception as e:
            logger.error(f"刷新交易日历失败: {e}")

    async def test_refresh_all_calendars():
        """测试刷新所有交易所的交易日历"""
        try:
            async for db in get_async_db():
                service = TradeCalendarService(db)
                await service.refresh_all_exchange_calendars()
                logger.info("刷新所有交易所的交易日历完成")
                break
        except Exception as e:
            logger.error(f"刷新所有交易日历失败: {e}")

    async def main():
        """运行所有测试"""
        try:
            # 基础功能测试
            await test_get_raw_trade_calendar()
            await test_get_raw_latest_trading_day()
            # 数据获取和保存测试
            await test_fetch_and_save_calendar()
            # 日期范围查询测试
            await test_get_raw_trade_calendar_with_date_range()
            # 更新机制测试
            await test_check_and_update_calendar()
            # 响应格式测试
            await test_get_trade_calendar_data()
            await test_get_latest_trading_day_data()
            # 刷新单个交易所的交易日历测试
            await test_refresh_trade_calendar()
            # 刷新所有交易所的交易日历测试
            await test_refresh_all_calendars()
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()

    asyncio.run(main())