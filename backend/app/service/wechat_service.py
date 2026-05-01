"""
微信 API 封装
- jscode2session 换取 openid
- access_token 获取（带缓存）
- 订阅消息发送
"""
import logging
import time
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# NOTE: access_token 缓存（进程级别）
_token_cache = {"value": "", "expire_at": 0}


async def code2session(code: str) -> dict:
    """
    通过 wx.login() 的 code 换取 openid 和 session_key
    """
    appid = settings.WECHAT_APPID
    secret = settings.WECHAT_SECRET

    if not appid or not secret:
        raise ValueError("未配置微信小程序 appid/secret")

    url = (
        f"https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={appid}&secret={secret}&js_code={code}"
        f"&grant_type=authorization_code"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()

    if data.get("openid"):
        return data

    logger.error("jscode2session 失败: %s", data)
    raise ValueError(f"微信登录失败: {data.get('errmsg', '未知错误')}")


async def get_access_token() -> str:
    """
    获取微信 access_token（带缓存）
    """
    global _token_cache

    if _token_cache["value"] and _token_cache["expire_at"] > time.time() + 60:
        return _token_cache["value"]

    appid = settings.WECHAT_APPID
    secret = settings.WECHAT_SECRET

    if not appid or not secret:
        raise ValueError("未配置微信小程序 appid/secret")

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if not data.get("access_token"):
        raise ValueError(f"获取 access_token 失败: {data.get('errmsg', '')}")

    _token_cache = {
        "value": data["access_token"],
        "expire_at": time.time() + int(data.get("expires_in", 7200)) - 120,
    }
    return _token_cache["value"]


async def send_subscribe_message(
    openid: str,
    template_id: str,
    data: dict,
    page: str = "",
) -> dict:
    """
    发送订阅消息
    返回微信响应 dict
    """
    try:
        access_token = await get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"

        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data,
        }
        if page:
            payload["page"] = page
            payload["miniprogram_state"] = "trial"

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            result = resp.json()

        logger.info("订阅消息发送结果: %s", result)
        return result
    except Exception as e:
        logger.error("订阅消息发送异常: %s", str(e))
        return {"errcode": -1, "errmsg": str(e)}
