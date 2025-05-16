from sqlalchemy import Column, String, Numeric, BigInteger
from sqlalchemy import Date
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP

class StockDailyOrm(Base):
    __tablename__ = 'stock_daily'  
    stock_code = Column(String(20), primary_key=True, comment='股票代码')
    date = Column(Date, primary_key=True, comment='日期') 
    open = Column(Numeric(10, 4), comment='开盘价') 
    high = Column(Numeric(10, 4), comment='最高价') 
    low = Column(Numeric(10, 4), comment='最低价') 
    close = Column(Numeric(10, 4), comment='收盘价')  
    change = Column(Numeric(10, 4), comment='涨跌额') 
    pct_chg = Column(Numeric(5, 2), comment='涨跌幅') 
    vol = Column(BigInteger, comment='成交量')
    amount = Column(Numeric(20, 2), comment='成交金额')
    qfq_factor = Column(Numeric(10, 6), comment='前复权因子')
    hfq_factor = Column(Numeric(10, 6), comment='后复权因子')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False,server_default=func.now(),onupdate=func.now(),comment='更新时间')

    def __repr__(self):
        return f"<StockDailyItem(stock_code={self.stock_code}, date={self.date})>"

if __name__=="__main__":
    from app.core.database import engine
    from loguru import logger
    Base.metadata.create_all(engine)  # 创建表结构
    logger.info("表结构创建成功")

    
