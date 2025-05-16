from pydantic import BaseModel, Field
from datetime import date as Date
from decimal import Decimal
from typing import List, Optional

# 股票日线数据请求模型
class StockDailyRequest(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    start_date: Optional[Date] = Field(None, description="起始日期")
    end_date: Optional[Date] = Field(None, description="结束日期")

# 股票日线数据基础模型
class StockDailyBase(BaseModel):
    date: Date = Field(..., description="交易日期")
    open: Decimal = Field(..., description="开盘价")
    high: Decimal = Field(..., description="最高价")
    low: Decimal = Field(..., description="最低价")
    close: Decimal = Field(..., description="收盘价")
    change: Decimal = Field(..., description="涨跌额")
    pct_chg: Decimal = Field(..., description="涨跌幅")
    vol: int = Field(..., description="成交量")
    amount: Decimal = Field(..., description="成交金额")
    qfq_factor: Decimal = Field(..., description="前复权因子")
    hfq_factor: Decimal = Field(..., description="后复权因子")
    
# 股票日线数据项模型
class StockDailyItem(StockDailyBase):
    stock_code: str = Field(..., description="股票代码")
    def to_orm(self):
        from app.models.stock_daily_orm import StockDailyOrm
        """
        将 Pydantic 模型转换为 ORM 模型
        """
        return StockDailyOrm(**self.model_dump())
    
# 股票日线数据响应项模型
class StockDailyResponseItem(StockDailyBase):
    pass

# 股票日线数据响应模型
class StockDailyResponse(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    data_count: int = Field(..., description="返回的日线数据数量")
    start_date: Date = Field(..., description="数据的起始日期")
    end_date: Date = Field(..., description="数据的结束日期")
    daily: List[StockDailyResponseItem] = Field(..., description="日线数据列表")