import akshare as ak
from app.schemas.stock_daily import StockDailyItem
import pandas as pd
from typing import Literal
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Optional
from app.utils.stock_utlis import check_stock_format
from app.utils.date_utlis import check_date_format,get_today
from app.external.exceptions import StockExternalDataError,StockExternalDataProcessingError
from loguru import logger
FIELD_MAPPING = {
            "日期": "date",
            "股票代码": "stock_code",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "vol",
            "成交额": "amount",
            "振幅": "amplitude",
            "涨跌幅": "pct_chg",
            "涨跌额": "change",
            "换手率": "turnover_rate"
        }
class StockDailyClient:
    """
    股票日线数据客户端
    """
    def __init__(self):
        pass

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _get_adjusted_close(code: str, start_date: str, end_date: str,adjust: Literal["qfq", "hfq"]="qfq") -> pd.DataFrame:
        """
        获取复权收盘价
        
        :param code: 股票代码，如 "600000"
        :param start_date: 开始日期，格式 "20220101"
        :param end_date: 结束日期，格式 "20230401"
        :param adjust: 复权方式，"qfq" 表示前复权，"hfq" 表示后复权
        :return: 包含复权收盘价的 DataFrame，索引为日期
        """
        try:
            adjust_daily =ak.stock_zh_a_hist(
                symbol=code,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            logger.debug(f"获取股票 {code} 的复权数据，时间范围：{start_date} 到 {end_date}")
            logger.debug(f"复权数据: {adjust_daily}")
            if adjust_daily.empty:
                logger.error(f"股票 {code} 的复权数据为空")
                return pd.DataFrame()
            logger.debug(f"获取股票 {code} 的原始已复权日线数据成功")
            logger.debug(f"原始已复权日线数据: {adjust_daily}")

            # 字段映射
            adjust_close = adjust_daily[['日期', '收盘']].rename(columns={'日期': 'date', '收盘':f'{adjust}_close'})
            adjust_close.set_index("date", inplace=True)
            logger.debug(f"加工股票 {code} 的复权数据成功")
            logger.debug(f"加工后的已复权数据: {adjust_close}")
            return adjust_close
        except Exception as e:
            logger.error(f"获取股票 {code} 的复权数据时发生错误: {e}")
            raise StockExternalDataError(f"获取股票 {code} 的复权数据失败", e)

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _get_raw_daily(code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票历史行情数据（来自 AkShare，单位保留为：手、元、%）。
        
        :param code: 股票代码，如 "600000"
        :param start_date: 开始日期，格式 "20220101"
        :param end_date: 结束日期，格式 "20230401"
        :return: List of StockDailyItem
        """
        logger.info(f"获取股票 {code} 的历史数据，时间范围：{start_date} 到 {end_date}")
        try:
            # 获取数据
            raw_daily = ak.stock_zh_a_hist(
                symbol=code,
                start_date=start_date,
                end_date=end_date,
            )
            # 如果数据为空，返回空列表
            if raw_daily.empty:
                return pd.DataFrame()
            logger.debug(f"获取股票 {code} 的原始未复权日线数据成功")
            logger.debug(f"原始未复权日线数据: {raw_daily}")
            # 字段映射
            raw_daily.rename(columns=FIELD_MAPPING, inplace=True) 
            raw_daily.set_index("date", inplace=True)
            raw_daily['pct_chg'] = raw_daily['pct_chg'].apply(lambda x: 0.0 if abs(x) > 100 else x)
            logger.debug(f"加工股票 {code} 的未复权数据成功")
            logger.debug(f"加工后的未复权数据: {raw_daily}")
            return raw_daily
        except ValueError as e:
            logger.error(f"获取股票 {code} 原始数据时遇到日期格式错误: {e}")
            raise StockExternalDataError(f"获取股票 {code} 原始数据时遇到日期格式错误: {e}", e)
        except Exception as e:
            logger.error(f"获取股票 {code} 原始数据时遇到未知错误: {e}")
            raise StockExternalDataError(f"获取股票 {code} 原始数据时遇到未知错误:{e}", e)
    
    @staticmethod
    async def _get_stock_daily(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票的历史行情数据（来自 AkShare，单位保留为：手、元、%）。
        """
        try:
            if not check_stock_format(code):
                logger.error(f"股票代码格式错误: {code}")
                raise ValueError(f"股票代码格式错误: {code}")
            if not start_date:
                start_date = "19901219"
            elif not check_date_format(start_date):
                logger.error(f"开始日期格式错误: {start_date}")
                raise ValueError(f"开始日期格式错误: {start_date}")
            if not end_date:
                end_date = get_today()
            elif not check_date_format(end_date):
                logger.error(f"结束日期格式错误: {end_date}")
                raise ValueError(f"结束日期格式错误: {end_date}")
            logger.debug(f"同步获取股票 {code} 的前复权、后复权与未复权日线数据中，时间范围：{start_date} 到 {end_date}")
            raw_daily, qfq_close, hfq_close = await asyncio.gather(
            StockDailyClient._get_raw_daily(code, start_date, end_date),
            StockDailyClient._get_adjusted_close(code, start_date, end_date, "qfq"),
            StockDailyClient._get_adjusted_close(code, start_date, end_date, "hfq"),
            )

            if raw_daily is None or raw_daily.empty:
                logger.error(f"股票 {code} 无法获取原始数据")
                raise StockExternalDataError(f"股票 {code} 无法获取原始数据")
            
            if qfq_close is None or qfq_close.empty:
                logger.error(f"股票 {code} 无法获取前复权数据")
                raise StockExternalDataError(f"股票 {code} 无法获取前复权数据")
            
            if hfq_close is None or hfq_close.empty:
                logger.error(f"股票 {code} 无法获取后复权数据")
                raise StockExternalDataError(f"股票 {code} 无法获取后复权数据")
            
        except ValueError as ve:
            logger.error(f"获取数据时发生格式错误: {ve}")
            raise StockExternalDataError(f"获取数据时发生格式错误: {ve}",ve)
        except StockExternalDataError as se:
            raise se
        except Exception as e:
            raise StockExternalDataError(f"发生未知错误: {e}",e)
        try:
            stock_daily = StockDailyClient._merge_and_validate_stock_daily(raw_daily, qfq_close, hfq_close, code)
            # 计算前复权因子
            stock_daily["qfq_factor"] = stock_daily["qfq_close"] / stock_daily["close"]
            # 计算后复权因子
            stock_daily["hfq_factor"] = stock_daily["hfq_close"] / stock_daily["close"]
            # 重置索引以便转换日期格式
            stock_daily = stock_daily.reset_index()
            stock_daily["date"] = pd.to_datetime(stock_daily["date"]).dt.date 
        except Exception as e:
            logger.error(f"数据处理时发生错误: {e}")
            raise StockExternalDataProcessingError(f"数据处理时发生错误: {e}",e)
        except StockExternalDataProcessingError as se:
            raise se
        return stock_daily
    
    @staticmethod
    def _merge_and_validate_stock_daily(raw_daily: pd.DataFrame, qfq_close: pd.DataFrame, hfq_close: pd.DataFrame, code: str) -> pd.DataFrame:
        """
        合并前复权、后复权数据，并校验 'close' 列是否有缺失或异常值。
        
        Args:
            raw_daily (pd.DataFrame): 原始未复权数据
            qfq_close (pd.DataFrame): 前复权收盘价数据
            hfq_close (pd.DataFrame): 后复权收盘价数据
            code (str): 股票代码，用于日志打印
        
        Returns:
            pd.DataFrame: 合并后的股票数据
        """
        # 通过日期对齐合并前复权、后复权数据
        stock_daily = raw_daily.join(qfq_close)
        stock_daily = stock_daily.join(hfq_close)
        
        logger.debug(f"合并股票 {code} 的前复权、后复权与未复权数据成功")
        logger.debug(f"合并后的数据: {stock_daily}")

        # 检查 'close' 列是否存在缺失值或者为0的情况
        bad_close_rows = raw_daily[raw_daily['close'].isnull() | (raw_daily['close'] == 0)]
        logger.debug(f"检查未复权数据的收盘价是否出现缺失/异常值的问题")

        if not bad_close_rows.empty:
            logger.error(f"股票 {code} 的 'close' 列存在缺失值或为0的情况，数量: {bad_close_rows.shape[0]}")
            raise StockExternalDataError(f"股票 {code} 的 'close' 列存在缺失值或为0，数量: {bad_close_rows.shape[0]}")
        else:
            logger.debug(f"股票 {code} 的 'close' 列没有缺失值或为0的情况，合并成功")

        return stock_daily

    @staticmethod
    def _daily_to_pydantic(stock_daily: pd.DataFrame) -> list[StockDailyItem]:
        """
        将 DataFrame 转换为 Pydantic 模型列表
        """
        records = stock_daily.to_dict(orient="records")
        result = []
        for item in records:
            try:
                result.append(StockDailyItem(**item))
            except Exception as e:
                logger.error(f"跳过错误数据: {e} → {item}")
                continue
                
        return result

    @staticmethod
    async def get_daily_items(code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[StockDailyItem]:
        """
        获取股票的历史行情数据（来自 AkShare，单位保留为：手、元、%）。
        """
        stock_daily = await StockDailyClient._get_stock_daily(code, start_date, end_date)
        if stock_daily.empty:
            return []
        return StockDailyClient._daily_to_pydantic(stock_daily)

if __name__ == "__main__":
    async def main():
        try:
            client= StockDailyClient()
            code = "300059"
            start_date = "20240101"
            end_date = "20240401"
            data = await client.get_daily_items(code, start_date, end_date)
            # data = await client.get_daily_items(code)
            for item in data:
                logger.info(item)
        except Exception as e:
            logger.error(f"运行测试时发生错误: {e}")
    # 运行测试
    asyncio.run(main())
