"""
通用响应模型与基类
"""
from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginatedData(BaseModel):
    """分页响应数据"""
    list: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
