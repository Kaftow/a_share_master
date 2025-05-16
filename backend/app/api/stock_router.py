from fastapi import APIRouter, Body, Depends
from app.services.stock_daily_service import StockDailyService , StockDailyServiceError
from app.services.stock_info_service import StockInfoService, StockInfoServiceError
from app.schemas.stock_daily import StockDailyRequest
from app.schemas.stock_info import StockInfoRequest
from app.core.database import get_async_db
from app.schemas.api_response import APIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.utils.response_utils import success_response, error_response
from app.utils.auth_utils import is_user_authenticated

router = APIRouter(prefix="/stock", tags=["股票数据接口"])

async def get_stock_daily_service(
    db_session: AsyncSession = Depends(get_async_db)
) -> StockDailyService:
    return StockDailyService(db_session)

async def get_stock_info_service(
    db_session: AsyncSession = Depends(get_async_db)
) -> StockInfoService:
    return StockInfoService(db_session)

@router.post("/daily", response_model=APIResponse)
async def get_stock_daily_data(
    request: StockDailyRequest = Body(...),  # 请求体为 StockDailyRequest 类型
    service: StockDailyService = Depends(get_stock_daily_service),  # 注入 StockDailyService 实例
    authenticated: bool = Depends(is_user_authenticated)
):
    """
    获取股票日线数据
    - request: StockDailyRequest 包含用户传入的股票代码和日期范围
    - service: StockDailyService 作为依赖注入
    - authenticated: 是否通过身份验证
    
    """
    if not authenticated:
        return error_response(message="未通过身份验证，请先登录！")
    stock_code = request.stock_code
    start_date = request.start_date
    end_date = request.end_date
    
    # 调用服务获取数据
    try:
        daily_data = await service.get_daily_data(stock_code, start_date, end_date)
        logger.info(f"成功获取股票 {stock_code} 的日线数据")
        # 构造 APIResponse 返回
        response = success_response(data=daily_data,message="成功获取股票日线数据")
        return response

    except StockDailyServiceError as e:
        # 错误处理，返回错误响应
        logger.error(f"获取股票日线数据时日线服务出现问题: {e}")
        response = error_response(error=e,message="日线服务出现问题失败")
        return response
    except Exception as e:
        # 捕获其他异常
        logger.error(f"获取股票日线数据时发生未知错误: {e}")
        # 返回错误响应
        response = error_response(error=e)
        return response
    
@router.post("/info", response_model=APIResponse)
async def get_stock_info_data(
    request: StockInfoRequest = Body(...),  # 请求体为 StockInfoRequest 类型
    service: StockInfoService = Depends(get_stock_info_service),  # 注入 StockInfoService 实例
    authenticated: bool = Depends(is_user_authenticated)
):
    """
    获取指定股票的基本信息
    - request: StockInfoRequest 包含股票代码
    - service: StockInfoService 作为依赖注入
    - authenticated: 是否通过身份验证
    """
    if not authenticated:
        return error_response(message="未通过身份验证，请先登录！")
    stock_code = request.stock_code  # 获取请求中的股票代码

    # 调用服务获取股票信息数据
    try:
        stock_info_data = await service.get_info_data(stock_code)
        # 构造 APIResponse 返回
        response = success_response(data=stock_info_data, message="成功获取股票基本信息")
        return response
    
    except StockInfoServiceError as e:
        # 错误处理，返回错误响应
        logger.error(f"获取股票基本信息时服务出现问题: {e}")
        # 返回错误响应
        response = error_response(error=e,message="个股基本信息服务出现问题失败")
        return response
    except Exception as e:
        # 捕获其他异常
        logger.error(f"获取股票基本信息时发生未知错误: {e}")
        # 返回错误响应
        response = error_response(error=e)
        return response



