from pydantic import BaseModel
from typing import Any

# 状态信息模型
class StatusInfo(BaseModel):
    message: str
    detail: dict

# API响应模型
class APIResponse(BaseModel):
    status: int
    data: Any
    statusInfo: StatusInfo