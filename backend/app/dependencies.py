"""
FastAPI 依赖注入
- 从 JWT Token 中提取当前用户身份
- 管理员权限校验
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Header

from app.utils.security import decode_access_token
from app.database import get_collection

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    从 Authorization: Bearer <token> 中解析当前用户
    返回 { "openid": "...", "user_id": "..." }
    所有需要登录的接口都通过此依赖注入
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或 Token 无效")

    token = authorization[7:]
    payload = decode_access_token(token)
    if not payload or "openid" not in payload:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")

    return {
        "openid": payload["openid"],
        "user_id": payload.get("user_id", ""),
    }


async def get_current_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    管理员权限校验
    1. 检查配置中的 ADMIN_OPENIDS 白名单
    2. 检查数据库中的 role === 'admin'
    """
    openid = current_user["openid"]
    from app.config import settings
    
    # 优先检查配置文件白名单
    if settings.ADMIN_OPENIDS and openid in settings.ADMIN_OPENIDS:
        current_user["role"] = "admin"
        return current_user

    users_col = get_collection("sign_users")
    user = await users_col.find_one({"openid": openid})

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")

    current_user["role"] = "admin"
    current_user["user_id"] = str(user["_id"])
    return current_user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """
    可选的用户身份解析（部分接口登录/未登录均可访问）
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]
    payload = decode_access_token(token)
    if not payload or "openid" not in payload:
        return None

    return {
        "openid": payload["openid"],
        "user_id": payload.get("user_id", ""),
    }
