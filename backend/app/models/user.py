"""
用户相关数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="wx.login() 获取的 code")


class LoginResponse(BaseModel):
    """登录响应"""
    _id: str = ""
    openid: str = ""
    role: str = "user"
    token: str = Field("", description="JWT Token")


class UserInfo(BaseModel):
    """用户信息"""
    _id: str = ""
    openid: str = ""
    role: str = "user"


class AdminCheckResponse(BaseModel):
    """管理员检查响应"""
    is_admin: bool = False
