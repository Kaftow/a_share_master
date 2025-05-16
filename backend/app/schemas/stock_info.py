from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# 个股信息请求模型
class StockInfoRequest(BaseModel):
    stock_code: str = Field(..., description="股票代码")

# 行业信息模型
class Industry(BaseModel):
    ind_code: str
    ind_name: str

# 个股信息基础模型
class StockInfoBase(BaseModel):
    exchange_code: str = Field(..., description="所在交易所代码")
    exchange_name: str = Field(..., description="所在交易所名称")
    org_id: Optional[str] = Field(None, description="机构 ID")
    org_name_cn: Optional[str] = Field(None, description="中文全称")
    org_short_name_cn: Optional[str] = Field(None, description="中文简称")
    org_name_en: Optional[str] = Field(None, description="英文全称")
    org_short_name_en: Optional[str] = Field(None, description="英文简称")
    main_operation_business: Optional[str] = Field(None, description="主营业务")
    operating_scope: Optional[str] = Field(None, description="经营范围")
    district_encode: Optional[str] = Field(None, description="地区编码")
    org_cn_introduction: Optional[str] = Field(None, description="公司简介")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    general_manager: Optional[str] = Field(None, description="总经理")
    secretary: Optional[str] = Field(None, description="董事会秘书")
    established_date: Optional[date] = Field(None, description="成立日期")
    reg_asset: Optional[Decimal] = Field(None, description="注册资本")
    staff_num: Optional[int] = Field(None, description="员工人数")
    telephone: Optional[str] = Field(None, description="电话")
    postcode: Optional[str] = Field(None, description="邮编")
    fax: Optional[str] = Field(None, description="传真")
    email: Optional[str] = Field(None, description="邮箱")
    org_website: Optional[str] = Field(None, description="官网")
    reg_address_cn: Optional[str] = Field(None, description="注册地址（中文）")
    office_address_cn: Optional[str] = Field(None, description="办公地址（中文）")
    currency_encode: Optional[str] = Field(None, description="币种编码")
    currency: Optional[str] = Field(None, description="币种")
    listed_date: Optional[date] = Field(None, description="上市日期")
    provincial_name: Optional[str] = Field(None, description="省份")
    actual_controller: Optional[str] = Field(None, description="实际控制人")
    classi_name: Optional[str] = Field(None, description="企业类型")
    pre_name_cn: Optional[str] = Field(None, description="前身公司")
    chairman: Optional[str] = Field(None, description="董事长")
    executives_nums: Optional[int] = Field(None, description="高管人数")
    actual_issue_vol: Optional[Decimal] = Field(None, description="实际发行量")
    issue_price: Optional[Decimal] = Field(None, description="发行价")
    actual_rc_net_amt: Optional[Decimal] = Field(None, description="募集净额")
    pe_after_issuing: Optional[Decimal] = Field(None, description="发行后市盈率")
    online_success_rate_of_issue: Optional[Decimal] = Field(None, description="网上申购中签率")
    affiliate_industry: Optional[Industry] = Field(default=None, description="关联行业")

# 个股信息项模型
class StockInfoItem(StockInfoBase):
    stock_code: str = Field(..., description="股票代码")
    def to_orm(self):
        from app.models.stock_info_orm import StockInfoOrm
        """
        将 Pydantic 模型转换为 ORM 模型
        """
        return StockInfoOrm(**self.model_dump())

# 个股信息响应项模型
class StockInfoResponseItem(StockInfoBase):
    class Config:
        from_attributes = True

# 个股信息响应模型
class StockInfoResponse(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    updated_at: datetime = Field(..., description="更新时间")
    info: StockInfoResponseItem = Field(..., description="个股信息")
