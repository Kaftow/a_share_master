from typing import Any
from app.schemas.api_response import APIResponse, StatusInfo


def success_response(data: Any = None, message: str = "操作成功", detail: dict = {}) -> APIResponse:
    return APIResponse(
        status=0,
        data=data,
        statusInfo=StatusInfo(
            message=message,
            detail=detail
        )
    )

def error_response(error: Exception, message: str = "出现未知错误", status_code: int | str = 1, detail: dict = {}) -> APIResponse:
    return APIResponse(
        status=status_code,
        data=None,
        statusInfo=StatusInfo(
            message=message,
            detail={
                "error": str(error),
                **detail
            }
        )
    )