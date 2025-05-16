from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.services.trade_calendar_service import TradeCalendarService, TradeCalendarServiceError
from app.core.database import get_async_db
from app.schemas.api_response import APIResponse
from app.schemas.trade_calendar import TradeCalendarRequest, ExchangeLastTradingDayRequest
from app.utils.response_utils import success_response, error_response
from app.utils.auth_utils import is_user_authenticated

router = APIRouter(prefix="/calendar",tags=["交易日历接口"])

async def get_trade_calendar_service(
    db_session: AsyncSession = Depends(get_async_db)
) -> TradeCalendarService:
    return TradeCalendarService(db_session)

@router.post("/trading-days", response_model=APIResponse)
async def get_trade_calendar_data(
    request: TradeCalendarRequest = Body(...),
    service: TradeCalendarService = Depends(get_trade_calendar_service),
    authenticated: bool = Depends(is_user_authenticated)
):
    """
    获取指定交易所的交易日历数据
    - request: TradeCalendarRequest 包含交易所代码和日期范围
    - service: TradeCalendarService 作为依赖注入
    - authenticated: 是否通过身份验证
    """
    if not authenticated:
        return error_response(message="未通过身份验证，请先登录！")
    try:
        calendar_data = await service.get_trade_calendar_data(
            request.exchange_code,
            request.start_date,
            request.end_date
        )
        logger.info(f"成功获取交易所 {request.exchange_code} 的交易日历数据")
        return success_response(data=calendar_data,message="成功获取交易日历数据")
    except TradeCalendarServiceError as e:
        logger.error(f"获取交易日历数据时服务出现问题: {e}")
        return error_response(error=e, message="交易日历服务出现问题")

    except Exception as e:
        logger.error(f"获取交易日历数据时发生未知错误: {e}")
        return error_response(error=e)

@router.post("/latest-trading-day", response_model=APIResponse)
async def get_latest_trading_day(
    request: ExchangeLastTradingDayRequest = Body(...),
    service: TradeCalendarService = Depends(get_trade_calendar_service),
    authenticated: bool = Depends(is_user_authenticated)
):
    """
    获取指定交易所的最新交易日
    - request: ExchangeLastTradingDayRequest 包含交易所代码
    - service: TradeCalendarService 作为依赖注入
    - authenticated: 是否通过身份验证
    """
    if not authenticated:
        return error_response(message="未通过身份验证，请先登录！")
    try:
        latest_day = await service.get_latest_trading_day_data(request.exchange_code)
        logger.info(f"成功获取交易所 {request.exchange_code} 的最新交易日")
        
        return success_response(data=latest_day, message="成功获取最新交易日")
    except TradeCalendarServiceError as e:
        logger.error(f"获取最新交易日时服务出现问题: {e}")
        return error_response(error=e, message="交易日历服务出现问题")
    except Exception as e:
        logger.error(f"获取最新交易日时发生未知错误: {e}")
        return error_response(error=e)
