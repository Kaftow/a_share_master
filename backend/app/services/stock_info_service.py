from typing import Optional
from app.models.stock_info_orm import StockInfoOrm
from app.schemas.stock_info import StockInfoItem, StockInfoResponse,StockInfoResponseItem,Industry
from app.repositories.stock_info_repository import StockInfoRepository, StockInfoRepositoryError
from app.external.stock_info import StockInfoClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from decimal import Decimal
import json
from app.external.exceptions import StockExternalDataError, StockExternalDataProcessingError
from loguru import logger
from app.core.cache_utlis import redis_cache

class StockInfoServiceError(Exception):
    """个股信息服务异常"""
    pass

class StockInfoService:
    DATE_FORMAT = "%Y%m%d"
    MAX_AGE= timedelta(days=1)
    def __init__(self, db_session: AsyncSession,max_age: timedelta = timedelta(days=1)):
        self._repository = StockInfoRepository(db_session)
        self._client = StockInfoClient()
        self._max_age=max_age
        
    @redis_cache(ttl=3600)
    async def get_info_data(
        self,
        stock_code: str
    ) -> StockInfoResponse:
        """
        获取指定股票代码和日期范围的个股信息数据，并返回 JSON 格式。
        如果数据库中没有完整的数据，则从外部接口获取并保存。
        """
        # 获取原始数据
        raw_data = await self.get_raw_info_data(stock_code)
        # 将 ORM 模型转换为 StockInfoResponse 模型 
        info_data = self._convert_to_response(raw_data)
        return info_data

    async def get_raw_info_data(
        self,
        stock_code: str
    ) -> StockInfoOrm:
        """
        获取指定股票代码和日期范围的股票日线数据。
        如果数据库中没有完整的数据，则从外部接口获取并保存。
        """
        try:
            # 查询数据库中的数据
            existing_record = await self._repository.find_stock_info(stock_code)
            if not existing_record or self._is_stock_info_expired(existing_record):
                logger.info(f"数据库中没有找到股票 {stock_code} 的数据，或数据已过期，准备从外部接口获取")
                # 从外部接口获取数据
                stock_info_item = await self._client.get_info_item(stock_code)
                logger.info(f"从外部接口获取股票 {stock_code} 的数据成功")
                if not stock_info_item:
                    logger.error(f"获取股票 {stock_code} 的数据失败")
                    raise StockExternalDataError(f"获取股票 {stock_code} 的数据失败")
                # 将 Pydantic 模型转换为 ORM 模型
                orm_item = stock_info_item.to_orm()
                # 保存到数据库
                await self._repository.save_stock_info(orm_item)
                logger.info(f"保存股票 {stock_code} 的数据到数据库成功")
                # 重新查询数据库以获取完整数据
                existing_record = await self._repository.find_stock_info(stock_code)
            return existing_record
        except StockInfoRepositoryError as e:
            logger.error(f"数据交互时候出现错误: {e}")
            raise StockInfoServiceError(f"数据交互时候出现错误，股票代码: {stock_code}, 错误: {e}") from e
        except StockExternalDataError as e:
            logger.error(f"外部数据获取失败: {e}")
            raise StockInfoServiceError(f"外部数据获取失败，股票代码: {stock_code}, 错误: {e}") from e
        except StockExternalDataProcessingError as e:
            logger.error(f"外部数据处理失败: {e}")
            raise StockInfoServiceError(f"外部数据处理失败，股票代码: {stock_code}, 错误: {e}") from e
        except StockInfoServiceError as e:
            raise e
        except Exception as e:
            logger.error(f"服务内部出现未知错误: {e}")
            raise StockInfoServiceError(f"服务内部出现未知错误，股票代码: {stock_code}, 错误: {e}") from e
        
    @staticmethod
    def _convert_to_response(stock_info: StockInfoOrm) -> StockInfoResponse:
        try:
            if not stock_info:
                return None

            # 提取 ORM 字段为字典
            info_data = {}
            for column in stock_info.__table__.columns:
                if column.name not in ['stock_code','updated_at']:
                    value = getattr(stock_info, column.name)
                    if column.name == 'affiliate_industry':
                        info_data[column.name] = StockInfoService._convert_affiliate_industry(value)
                    else:
                        info_data[column.name] = StockInfoService._convert_value(value)

            # 构造 info 对象（StockInfoResponseItem）
            info = StockInfoResponseItem(**info_data)

            # 构造最终响应（StockInfoResponse）
            return StockInfoResponse(
                stock_code=stock_info.stock_code,
                updated_at=stock_info.updated_at,
                info=info
            )

        except Exception as e:
            logger.error(f"转换数据时发生错误: {e}")
            raise StockInfoServiceError(f"转换数据时发生错误: {e}", e)
    
    @staticmethod
    def _convert_value(value):
        """转换不同类型的字段值为适合 JSON 的格式"""
        # 处理 Decimal 类型字段
        if isinstance(value, Decimal):
            return str(value)  # 转换为字符串，避免 JSON 无法处理 Decimal 类型
        
        # 处理 DateTime 类型字段
        elif isinstance(value, datetime):
            return value.isoformat()  # 转换为 ISO 格式字符串

        # 处理 JSON 类型字段（字典或列表）
        elif isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)  # 将 JSON 字段转换为字符串

        # 对于其他类型，直接返回原值
        return value
    
    @staticmethod
    def _convert_affiliate_industry(value: str | dict) -> Optional[Industry]:
        """转换 affiliate_industry 字段为 Industry 实例"""
        if isinstance(value, str):  # 如果是字符串形式的 JSON
            try:
                value = json.loads(value)  # 将字符串解析为字典
                return Industry(**value)  # 使用 Pydantic 模型转换
            except json.JSONDecodeError:
                return None  # 如果无法解析 JSON，返回 None
        elif isinstance(value, dict):  # 如果已经是字典，直接转换为 Industry 实例
            return Industry(**value)
        return None
    
    def _is_stock_info_expired(self, existing_record) -> bool:
        """判断股票信息是否过期。

        Args:
            existing_record: 包含 updated_at 字段的 ORM 实例。
            max_age: 允许的最大时间差（默认一天）。

        Returns:
            bool: True 表示数据已过期，False 表示仍然有效。
        """

        updated_at: Optional[datetime] = getattr(existing_record, 'updated_at', None)
        if updated_at is None:
            return True  # 没有更新时间字段，视为过期

        return datetime.now() - updated_at > self._max_age


if __name__ == "__main__":
    import asyncio
    from app.core.database import get_async_db
    from fastapi.responses import JSONResponse
    async def test_get_raw_info_data():
        """测试获取个股信息数据"""
        try:
            async for db in get_async_db():

                service = StockInfoService(db)
                stock_code = "000001"
                stock_data = await service.get_raw_info_data(stock_code)
                logger.info(f"测试结果：已找到股票代码为{stock_code}的条数据")
                logger.info(stock_data)
                break
        except Exception as e:
            logger.error(f"获取股票数据时发生错误: {e}")

    async def test_get_info_data():
        """测试获取个股信息数据"""
        try:
            async for db in get_async_db():
                service = StockInfoService(db)
                stock_code = "000001"
                info_data = await service.get_info_data(stock_code)
                logger.info(f"测试结果：已找到股票代码为{stock_code}的个股信息数据")
                logger.info(info_data)
                logger.info(JSONResponse(content=info_data.model_dump(mode="json")).body.decode("utf-8"))
                break
        except Exception as e:
            logger.error(f"获取个股信息时发生错误: {e}")
    async def main():
        """运行测试"""
        try:
            await test_get_raw_info_data()
            await test_get_info_data()
        finally:
            from app.core.database import async_engine
            await async_engine.dispose()

    asyncio.run(main())