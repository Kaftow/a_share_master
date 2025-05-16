from sqlalchemy import Column, String, Date, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class TradeCalendarOrm(Base):
    __tablename__ = 'trade_calendar'
    exchange_code = Column(String(10), primary_key=True, comment="交易所代码，如SH（上交所）、SZ（深交所）、BJ（北交所）")
    trade_date = Column(Date, primary_key=True, comment="交易日")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return f"<TradeCalendar(exchange_code={self.exchange_code}, trade_date={self.trade_date})>"

if __name__ == "__main__":
    from app.core.database import engine
    from loguru import logger
    logger.info("交易日历表结构创建成功")
