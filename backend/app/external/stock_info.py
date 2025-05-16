import akshare as ak
from app.schemas.stock_info import StockInfoItem
import pandas as pd
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Optional
from app.utils.stock_utlis import get_stock_exchange_code,get_exchange_name_by_code
from app.external.exceptions import StockExternalDataError,StockExternalDataProcessingError
from datetime import datetime
from app.external.xq_token import XueqiuTokenProvider
from loguru import logger

class StockInfoClient:
    def __init__(self, token_provider: Optional[XueqiuTokenProvider] = None):
        """
        初始化 StockInfoClient，需要提供一个 token 提供者

        :param token_provider: XueqiuTokenProvider 实例，如果为 None 则会创建一个新的实例
        """
        self._token_provider = token_provider or XueqiuTokenProvider()
    
    async def _get_xq_token(self) -> str:
        """
        获取雪球的 token
        :return: 雪球的 token
        """
        xq_token = self._token_provider.get_token()
        if not xq_token:
            raise StockExternalDataError("获取雪球token失败")
        return xq_token

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _get_raw_info(self,xq_symbol: str) -> pd.DataFrame:
        """
        获取个股信息，调用雪球的接口
        
        :param xq_symbol: 雪球的股票代码，如 "600000"
        :param xq_token: 雪球 API 的 Token
        :return: 返回包含个股信息的 DataFrame 或 None
        """
        try:
            xq_token = await self._get_xq_token()
            raw_daily =ak.stock_individual_basic_info_xq(symbol=xq_symbol,token=xq_token)
            return raw_daily
        except Exception as e:
            logger.error(f"获取个股信息失败: {e}")
            raise StockExternalDataError(f"获取个股信息失败: {e}",e)
        
        
    async def _get_stock_info(self,code: str) -> pd.DataFrame:
        """
        获取个股信息，调用雪球的接口，并将交易所代码和交易所全称加入返回的数据。
        
        :param code: 股票代码，如 "600000"
        :param xq_token: 雪球 API 的 Token
        :return: 返回包含个股信息和交易所信息的 DataFrame 或 None
        """
        try:
            # 获取股票交易所代码（
            exchange_code = get_stock_exchange_code(code)
            if exchange_code is None:
                raise ValueError(f"无效的股票代码: {code}")

            # 拼接雪球股票代码
            xq_symbol = f"{exchange_code}{code}"
            stock_info= await self._get_raw_info(xq_symbol)
            exchange_name = get_exchange_name_by_code(exchange_code)
            stock_info = pd.concat([
                pd.DataFrame([
                    {"item": "stock_code", "value": code},
                    {"item": "exchange_code", "value": exchange_code},
                    {"item": "exchange_name", "value": exchange_name},
                ]),
                stock_info,
            ], ignore_index=True)
            # 返回股票信息
            return stock_info
        except StockExternalDataError as e:
            logger.error(f"获取个股信息失败: {e}")
            raise e
        except ValueError as ve:
            logger.error(f"无效的股票代码: {code}, 错误: {ve}")
            raise StockExternalDataError(f"无效的股票代码: {code}", ve)
        except Exception as e:
            logger.error(f"处理个股信息失败: {e}")
            raise StockExternalDataProcessingError(f"处理个股信息失败: {e}", e)
        
    @staticmethod
    def _info_to_pydantic(stock_info: pd.DataFrame) -> StockInfoItem:
        try:
            info_dict = pd.Series(stock_info["value"].values, index=stock_info["item"]).to_dict()

            for date_field in ["established_date", "listed_date"]:
                if info_dict.get(date_field):
                    try:
                        timestamp = int(info_dict[date_field])
                        info_dict[date_field] = datetime.fromtimestamp(timestamp / 1000).date()
                    except Exception:
                        info_dict[date_field] = None  
            return StockInfoItem(**info_dict)
        except Exception as e:
            logger.error(f"转换数据时发生错误: {e}")
            raise StockExternalDataProcessingError(f"转换数据时发生错误: {e}", e)


    async def get_info_item(self,code: str) -> StockInfoItem:
        """
        获取股票的个股信息，并转换为 Pydantic 模型。

        :param code: 股票代码，如 "600000"
        :param xq_token: 雪球 API 的 Token
        :return: 返回 StockInfoItem 模型实例
        """
        try:
            # 获取股票信息，调用 get_stock_info 获取个股信息
            stock_info = await self._get_stock_info(code)
            # 转换为 Pydantic 模型
            stock_info_item = StockInfoClient._info_to_pydantic(stock_info)
            return stock_info_item
        except Exception as e:
            logger.error(f"获取或转换个股信息时发生错误: {e}")
            raise StockExternalDataProcessingError(f"获取或转换个股信息时发生错误: {e}", e)


if __name__ == "__main__":
    import asyncio
    async def main():
        try:
            client = StockInfoClient()
            code = "000001"
            logger.info(f"\n开始测试股票代码: {code}")    
            logger.info("\n1. 测试获取原始股票信息...")
            exchange_code = get_stock_exchange_code(code)
            xq_symbol = f"{exchange_code}{code}"
            raw_info = await client._get_raw_info(xq_symbol)
            logger.info(f"原始信息:\n{raw_info}\n")
            logger.info("\n2. 测试获取处理后的股票信息...")
            stock_info = await client._get_stock_info(code)
            logger.info(f"处理后信息:\n{stock_info}\n")
            logger.info("\n3. 测试获取Pydantic模型...")
            stock_info_item = await client.get_info_item(code)
            logger.info(f"Pydantic模型:\n{stock_info_item}\n")
        except Exception as e:
            logger.error(f"\n测试过程中发生错误: {e}")
    asyncio.run(main())
