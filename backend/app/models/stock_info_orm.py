from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, JSON, TIMESTAMP
from app.core.database import Base
from sqlalchemy.sql import func

class StockInfoOrm(Base):
    __tablename__ = 'stock_info'
    stock_code = Column(String(20), primary_key=True, comment='股票代码')
    exchange_code = Column(String(10), comment='所在交易所代码')
    exchange_name = Column(String(10), comment='所在交易所名称')
    org_id = Column(String(50), nullable=True, comment='机构 ID')
    org_name_cn = Column(String(100), nullable=True, comment='中文全称')
    org_short_name_cn = Column(String(50), nullable=True, comment='中文简称')
    org_name_en = Column(String(100), nullable=True, comment='英文全称')
    org_short_name_en = Column(String(50), nullable=True, comment='英文简称')
    main_operation_business = Column(Text, nullable=True, comment='主营业务')
    operating_scope = Column(Text, nullable=True, comment='经营范围')
    district_encode = Column(String(20), nullable=True, comment='地区编码')
    org_cn_introduction = Column(Text, nullable=True, comment='公司简介')
    legal_representative = Column(String(50), nullable=True, comment='法定代表人')
    general_manager = Column(String(50), nullable=True, comment='总经理')
    secretary = Column(String(50), nullable=True, comment='董事会秘书')
    established_date = Column(DateTime, nullable=True, comment='成立日期')
    reg_asset = Column(Numeric(18, 2), nullable=True, comment='注册资本')
    staff_num = Column(Integer, nullable=True, comment='员工人数')
    telephone = Column(String(50), nullable=True, comment='电话')
    postcode = Column(String(20), nullable=True, comment='邮编')
    fax = Column(String(50), nullable=True, comment='传真')
    email = Column(String(100), nullable=True, comment='邮箱')
    org_website = Column(String(200), nullable=True, comment='官网')
    reg_address_cn = Column(String(200), nullable=True, comment='注册地址（中文）')
    office_address_cn = Column(String(200), nullable=True, comment='办公地址（中文）')
    currency_encode = Column(String(20), nullable=True, comment='币种编码')
    currency = Column(String(20), nullable=True, comment='币种')
    listed_date = Column(DateTime, nullable=True, comment='上市日期')
    provincial_name = Column(String(50), nullable=True, comment='省份')
    actual_controller = Column(String(100), nullable=True, comment='实际控制人')
    classi_name = Column(String(50), nullable=True, comment='企业类型')
    pre_name_cn = Column(String(100), nullable=True, comment='前身公司')
    chairman = Column(String(50), nullable=True, comment='董事长')
    executives_nums = Column(Integer, nullable=True, comment='高管人数')
    actual_issue_vol = Column(Numeric(18, 2), nullable=True, comment='实际发行量')
    issue_price = Column(Numeric(10, 4), nullable=True, comment='发行价')
    actual_rc_net_amt = Column(Numeric(18, 2), nullable=True, comment='募集净额')
    pe_after_issuing = Column(Numeric(10, 2), nullable=True, comment='发行后市盈率')
    online_success_rate_of_issue = Column(Numeric(5, 4), nullable=True, comment='网上申购中签率')
    affiliate_industry = Column(JSON, nullable=True, comment='关联行业')
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False,server_default=func.now(),onupdate=func.now(),comment='更新时间')
    
    def __repr__(self):
        return f"<StockInfoItem(stock_code={self.stock_code}, exchange_code={self.exchange_code}, org_name_cn={self.org_name_cn})>"
    
if __name__=="__main__":
    from app.core.database import engine
    from loguru import logger
    Base.metadata.create_all(engine)  # 创建表结构
    logger.info("表结构创建成功")