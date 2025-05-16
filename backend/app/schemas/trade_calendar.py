from pydantic import BaseModel, Field
from datetime import date
from typing import Literal, List,Optional
from app.models.trade_calendar_orm import TradeCalendarOrm

# 交易日历请求模型
class TradeCalendarRequest(BaseModel):
    exchange_code: Literal["SH", "SZ", "BJ"] = Field(..., description="交易所代码：SH（上交所）、SZ（深交所）、BJ（北交所）")
    start_date: Optional[date] = Field(None, description="起始日期")
    end_date: Optional[date] = Field(None, description="结束日期")

# 交易所最后交易日请求模型
class ExchangeLastTradingDayRequest(BaseModel):
    exchange_code: Literal["SH", "SZ", "BJ"] = Field(..., description="交易所代码：SH（上交所）、SZ（深交所）、BJ（北交所）")

# 交易日历基础模型
class TradeCalendarBase(BaseModel):
    exchange_code: Literal["SH", "SZ", "BJ"] = Field(..., description="交易所代码：SH（上交所）、SZ（深交所）、BJ（北交所）")
    trade_dates: List[date] = Field(..., description="所有交易日的集合")
    
# 交易日历项目模型
class TradeCalendarItem(TradeCalendarBase):
    def to_orm(self)-> List['TradeCalendarOrm']:
        # 将 trade_dates 中的每个日期转换成多个 ORM 对象
        return [TradeCalendarOrm(exchange_code=self.exchange_code, trade_date=trade_date) for trade_date in self.trade_dates]

# 交易日历响应项模型
class TradeCalendarResponseItem(TradeCalendarBase):
    pass

# 交易日历响应模型
class TradeCalendarResponse(TradeCalendarBase):
    total_count: int = Field(..., description="交易日总数")
    first_trade_date: date = Field(..., description="当前周期第一个交易日")
    last_trade_date: date = Field(..., description="当前周期最后一个交易日")

# 交易所最后交易日模型
class ExchangeLastTradingDayItem(BaseModel):
    exchange_code: Literal["SH", "SZ", "BJ"] = Field(..., description="交易所代码：SH（上交所）、SZ（深交所）、BJ（北交所）")
    last_trading_day: date = Field(..., description="最近一个交易日")

# 交易所最后交易日响应模型
class ExchangeLastTradingDayResponse(ExchangeLastTradingDayItem):
    pass

