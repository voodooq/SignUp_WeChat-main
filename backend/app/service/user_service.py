"""
用户业务逻辑
- 微信登录 + 自动注册
- 获取用户信息
- 管理员检查
"""
import logging

from app.repository import user_repo
from app.service import wechat_service
from app.utils.security import create_access_token
from app.utils.i18n import t

logger = logging.getLogger(__name__)


async def login_with_code(code: str) -> dict:
    """
    微信登录流程：
    1. 用 code 调用微信 jscode2session 换取 openid
    2. 查找或创建用户
    3. 签发 JWT Token
    """
    wx_res = await wechat_service.code2session(code)
    openid = wx_res["openid"]

    user = await user_repo.find_by_openid(openid)

    if user:
        # 老用户，更新登录时间
        user_id = str(user["_id"])
        await user_repo.update_login_time(user_id)
        role = user.get("role", "user")
    else:
        # 新用户，自动注册
        user_id = await user_repo.create_user(openid)
        role = "user"

    # 签发 JWT Token
    token = create_access_token({"openid": openid, "user_id": user_id})

    return {
        "code": 200,
        "message": t("login_success"),
        "data": {
            "_id": user_id,
            "openid": openid,
            "role": role,
            "token": token,
        },
    }


async def get_user_info(openid: str) -> dict:
    """获取用户信息"""
    user = await user_repo.find_by_openid(openid)
    if not user:
        return {"code": 404, "message": t("user_not_found")}

    return {
        "code": 200,
        "data": {
            "_id": str(user["_id"]),
            "openid": user["openid"],
            "role": user.get("role", "user"),
        },
    }


async def check_admin(openid: str) -> dict:
    """检查是否为管理员"""
    from app.config import settings
    # 优先检查配置文件白名单
    if settings.ADMIN_OPENIDS and openid in settings.ADMIN_OPENIDS:
        return {"code": 200, "data": {"is_admin": True}}

    user = await user_repo.find_by_openid(openid)
    if not user:
        return {"code": 404, "message": t("user_not_found")}

    return {
        "code": 200,
        "data": {"is_admin": user.get("role") == "admin"},
    }
