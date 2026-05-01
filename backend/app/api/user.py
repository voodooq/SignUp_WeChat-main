"""
用户相关 API 路由
"""
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.service import user_service
from app.models.user import LoginRequest

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.post("/login")
async def login(req: LoginRequest):
    """微信登录（code 换 token）"""
    return await user_service.login_with_code(req.code)


@router.get("/info")
async def get_info(current_user: dict = Depends(get_current_user)):
    """获取用户信息"""
    return await user_service.get_user_info(current_user["openid"])


@router.get("/check-admin")
async def check_admin(current_user: dict = Depends(get_current_user)):
    """检查管理员身份"""
    return await user_service.check_admin(current_user["openid"])
