import akshare as ak
import pandas as pd
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed
from app.utils.date_utlis import check_date_format,get_today
from app.external.exceptions import StockExternalDataError,StockExternalDataProcessingError
from loguru import logger
from datetime import date
from typing import Literal, Set, Optional,List
from app.schemas.trade_calendar import TradeCalendarItem,ExchangeLastTradingDayItem
#上交所最早上市的几只股票，从前到后分别是飞乐音响、方正科技、云赛智联、申华控股和豫园股份
SH_CODES={"600651","600601","600602","600653","600655"}
#深交所最早上市的几只股票，从前到后分别是平安银行、万科A、国华网安和ST星源
SZ_CODES={"000001","000002","000004","000005"}
#北交所最早上市的几只股票，从前到后分别是广咨国际、广脉科技、海希通讯、恒合股份和锦好医疗
BJ_CODES={"836892","838924","831305","832145","872925"}
class TradeCalendarClient:
    """
    交易日历客户端
    """
    EXCHANGE_REPRESENTATIVE_STOCKS = {
        "SH": SH_CODES,  # 上交所代表
        "SZ": SZ_CODES,  # 深交所代表
        "BJ": BJ_CODES,  # 北交所代表
    }
    def __init__(self):
        pass
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _get_one_stock_calendar(stock_code: str, start_date: Optional[str]=None, end_date: Optional[str]=None) -> Set[date]:
        """
        获取股票的交易日历（日期）

        :param code: 股票代码，例如 "600000"
        :param start_date: 起始日期，格式为 "YYYYMMDD"
        :param end_date: 结束日期，格式为 "YYYYMMDD"
        :return: 包含交易日期的 DataFrame，列名为 "date"
        :raises StockExternalDataError: 获取数据失败时抛出此异常
        """
        try:
            # 校验并设置日期格式
            if not start_date:
                start_date = "19901219"  # 默认从最早日期开始
            elif not check_date_format(start_date):
                logger.error(f"开始日期格式不正确: {start_date}")
                raise ValueError(f"开始日期格式不正确: {start_date}")
            
            if not end_date:
                end_date = get_today()  # 默认截至今天
            elif not check_date_format(end_date):
                logger.error(f"结束日期格式不正确: {end_date}")
                raise ValueError(f"结束日期格式不正确: {end_date}")

            # 获取股票日线数据
            stock_daily = ak.stock_zh_a_hist(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
            )

            logger.debug(f"获取股票 {stock_code} 从 {start_date} 到 {end_date} 的日线数据")
            if stock_daily.empty:
                logger.error(f"股票 {stock_code} 没有返回有效的日线数据")
                return set()  # 返回空集合

            logger.debug(f"成功获取股票 {stock_code} 的日线数据")
            # 提取日期列，转为 datetime.date 并去重成集合
            dates = set(pd.to_datetime(stock_daily['日期']).dt.date)
            logger.debug(f"成功处理股票 {stock_code} 的交易日集合，交易日数量: {len(dates)}")
            return dates

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 数据时发生错误: {e}")
            raise StockExternalDataError(f"获取股票 {stock_code} 的交易日历失败", e)
        
    @staticmethod
    async def _get_one_stock_last_trading_day(stock_code: str) -> date:
        """
        获取指定股票的最近交易日。

        :param code: 股票代码
        :return: 最近交易日，格式为 "YYYYMMDD"；如果没有数据则返回 None
        """
        # 获取股票的交易日历数据
        stock_calendar = await TradeCalendarClient._get_one_stock_calendar(stock_code)
        if not stock_calendar:
            logger.error(f"股票 {stock_code} 在指定日期范围内没有交易数据")
            raise StockExternalDataError(f"股票 {stock_code} 在指定日期范围内没有交易数据")
        # 找到最近的交易日，应该是日期集合中最大的一天
        last_tradng_day = max(stock_calendar)
        logger.debug(f"股票 {stock_code} 最近的交易日是: {last_tradng_day}")
        return last_tradng_day
    
    @staticmethod
    async def _get_exchange_trade_calendar(
        exchange_code: Literal["BJ", "SZ", "SH"],
        start_date: Optional[str]=None, 
        end_date: Optional[str]=None
    ) -> List[date]:
        """
        获取指定交易所的交易日历，返回所有代表股票的去重交易日期集合。

        :param exchange_code: 交易所代码，"BJ"、"SZ" 或 "SH"
        :param start_date: 起始日期，格式为 "YYYYMMDD"（可选）
        :param end_date: 结束日期，格式为 "YYYYMMDD"（可选）
        :return: 包含交易日期的去重日期集合，类型为 List[datetime.date]
        :raises ValueError: 如果交易所代码不正确或日期格式不正确
        """
        if exchange_code not in TradeCalendarClient.EXCHANGE_REPRESENTATIVE_STOCKS:
            raise ValueError(f"无效的交易所代码: {exchange_code}")
        stock_codes = TradeCalendarClient.EXCHANGE_REPRESENTATIVE_STOCKS[exchange_code]
        tasks = [
            TradeCalendarClient._get_one_stock_calendar(stock_code, start_date, end_date)
            for stock_code in stock_codes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_dates = set()
        for stock_code, result in zip(stock_codes, results):
            if isinstance(result, Exception):
                logger.error(f"获取股票 {stock_code} 的交易日历失败: {result}")
            else:
                all_dates.update(result)
        if all_dates:
            return sorted(all_dates)
        else:
            logger.error(f"交易所 {exchange_code} 的交易日历获取失败")
        raise StockExternalDataError(f"交易所 {exchange_code} 的交易日历全部拉取失败")
        
    @staticmethod
    async def _get_exchange_last_trading_day(exchange_code: Literal["BJ", "SZ", "SH"]) -> date:
        """
        获取指定交易所的最近交易日。

        :param exchange_code: 交易所代码，"BJ"、"SZ" 或 "SH"
        :return: 最近交易日，格式为 "YYYYMMDD"；如果没有数据则返回 None
        """
        # 获取该交易所的代表股票代码集合
        if exchange_code not in TradeCalendarClient.EXCHANGE_REPRESENTATIVE_STOCKS:
            raise ValueError(f"无效的交易所代码: {exchange_code}")
        codes = TradeCalendarClient.EXCHANGE_REPRESENTATIVE_STOCKS[exchange_code]
        last_trading_day = None  # 存储最近的交易日
        # 获取每只股票的最近交易日并进行比较
        for code in codes:
            try:
                # 使用已有的  _get_one_stock_last_trade_date 方法获取单只股票的最近交易日
                stock_last_trading_day = await TradeCalendarClient._get_one_stock_last_trading_day(code)
                if stock_last_trading_day:
                    if last_trading_day is None or stock_last_trading_day > last_trading_day:
                        last_trading_day = stock_last_trading_day
            except Exception as e:
                logger.error(f"拉取股票 {code} 的最近交易日失败: {e}")
        if last_trading_day:
            logger.debug(f"交易所 {exchange_code} 最近的交易日是: {last_trading_day}")
            return last_trading_day
        else:
            logger.error(f"交易所 {exchange_code} 没有找到交易日数据")
            raise StockExternalDataError(f"交易所 {exchange_code} 没有找到交易日数据")
        
    @staticmethod
    async def get_exchange_trade_calendar_item(
        exchange_code: Literal["BJ", "SZ", "SH"],
        start_date: Optional[str]=None, 
        end_date: Optional[str]=None) -> TradeCalendarItem:
        """
        将日期转换为 TradeCalendarItem 对象

        :param date: 日期对象
        :return: TradeCalendarItem 对象
        """
        raw_calendar = await TradeCalendarClient._get_exchange_trade_calendar(exchange_code, start_date, end_date)
        trade_calendar_item = TradeCalendarItem(
            exchange_code=exchange_code,
            trade_dates=raw_calendar
        )
        logger.debug(f"获取交易所 {exchange_code} 的TradeCalendarItem 对象交易日历成功")
        return trade_calendar_item
    
    @staticmethod
    async def get_exchange_last_trading_day_item(exchange_code: Literal["BJ", "SZ", "SH"]) -> ExchangeLastTradingDayItem:
        last_tradng_day=await TradeCalendarClient._get_exchange_last_trading_day(exchange_code)
        last_trading_day_item=ExchangeLastTradingDayItem(exchange_code=exchange_code,last_trading_day=last_tradng_day)
        return last_trading_day_item


# 测试代码

if __name__ == "__main__":
    import asyncio
    # 确保 `TradeCalendarClient` 被正确导入
    # 测试数据
    async def test_get_stock_calendar():
        """
        测试获取单只股票的交易日历
        """
        code = "600000"  # 测试股票代码，改为你需要测试的股票
        start_date = "20230101"
        end_date = "20230401"
        try:
            result = await TradeCalendarClient._get_one_stock_calendar(code, start_date, end_date)
            print(f"股票 {code} 的交易日历：", result)
        except StockExternalDataError as e:
            print(f"获取股票 {code} 交易日历时发生错误: {e}")

    async def test_get_one_stock_last_trading_day():
        """
        测试获取单只股票的最近交易日
        """
        code = "600000"  # 测试股票代码
        try:
            recent_trade_day = await TradeCalendarClient._get_one_stock_last_trading_day(code)
            print(f"股票 {code} 最近的交易日：", recent_trade_day)
        except StockExternalDataError as e:
            print(f"获取股票 {code} 最近交易日时发生错误: {e}")

    async def test_get_exchange_trade_calendar():
        """
        测试获取某个交易所的交易日历
        """
        exchange_code = "SH"  # 测试上海证券交易所
        start_date = "20230101"
        end_date = "20230401"
        try:
            trade_calendar = await TradeCalendarClient._get_exchange_trade_calendar(exchange_code, start_date, end_date)
            print(f"交易所 {exchange_code} 的交易日历：", trade_calendar)
        except StockExternalDataError as e:
            print(f"获取交易所 {exchange_code} 交易日历时发生错误: {e}")

    async def test_get_exchange_last_trading_day():
        """
        测试获取某个交易所的最近交易日
        """
        exchange_code = "SH"  # 测试上海证券交易所
        try:
            recent_trade_day = await TradeCalendarClient._get_exchange_last_trading_day(exchange_code)
            print(f"交易所 {exchange_code} 最近的交易日：", recent_trade_day)
        except StockExternalDataError as e:
            print(f"获取交易所 {exchange_code} 最近交易日时发生错误: {e}")

    async def test_get_exchange_trade_calendar_item():
        """
        测试获取并转换为 TradeCalendarItem 对象
        """
        exchange_code = "SH"  # 测试上海证券交易所
        start_date = "20230101"
        end_date = "20230401"
        try:
            trade_calendar_item = await TradeCalendarClient.get_exchange_trade_calendar_item(exchange_code, start_date, end_date)
            print(f"交易所 {exchange_code} 的交易日历（TradeCalendarItem 对象）：", trade_calendar_item)
        except StockExternalDataError as e:
            print(f"获取交易所 {exchange_code} 的 TradeCalendarItem 时发生错误: {e}")

    async def test_get_exchange_last_trading_day_item():
        """
        测试获取并转换为 ExchangeLastTradingDayItem 对象
        """
        exchange_code = "SH"  # 测试上海证券交易所
        try:
            last_trading_day_item = await TradeCalendarClient.get_exchange_last_trading_day_item(exchange_code)
            print(f"交易所 {exchange_code} 的最近交易日（ExchangeLastTradingDayItem 对象）：", last_trading_day_item)
        except StockExternalDataError as e:
            print(f"获取交易所 {exchange_code} 的 ExchangeLastTradingDayItem 时发生错误: {e}")
    # 测试各个方法
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_get_stock_calendar())
    loop.run_until_complete(test_get_one_stock_last_trading_day())
    loop.run_until_complete(test_get_exchange_trade_calendar())
    loop.run_until_complete(test_get_exchange_last_trading_day())
    loop.run_until_complete(test_get_exchange_trade_calendar_item())
    loop.run_until_complete(test_get_exchange_last_trading_day_item())
