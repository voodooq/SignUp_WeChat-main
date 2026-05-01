"""
支付业务逻辑（第二阶段完善，当前提供模拟支付）
"""
import logging
import time

from app.config import settings
from app.repository import registration_repo, event_repo

logger = logging.getLogger(__name__)


def _normalize_fee_to_fen(fee_raw) -> int:
    try:
        num = float(fee_raw)
        if num <= 0:
            return 0
        return int(num) if num == int(num) else round(num * 100)
    except (TypeError, ValueError):
        return 0


def _normalize_event_list(input_val) -> list:
    if isinstance(input_val, list):
        return [str(i).strip() for i in input_val if str(i).strip()]
    if isinstance(input_val, str):
        import re
        return [s.strip() for s in re.split(r"[、,，;；\s]+", input_val) if s.strip()]
    return []


def _extract_event_names(reg: dict) -> list:
    required = (reg.get("required_event") or "").strip()
    optional = _normalize_event_list(reg.get("optional_events"))
    from_name = _normalize_event_list(reg.get("event_name"))
    merged = [required] + optional + from_name
    return list(dict.fromkeys([n for n in merged if n]))


async def create_order(openid: str, registration_id: str) -> dict:
    """创建支付订单"""
    reg = await registration_repo.find_by_id(registration_id)
    if not reg:
        return {"code": 404, "message": "报名记录不存在"}
    if reg.get("openid") != openid:
        return {"code": 403, "message": "无权操作此报名记录"}
    if reg.get("payment_status") == "paid":
        return {"code": 409, "message": "该报名已缴费，无需重复支付"}
    if reg.get("payment_status") == "admin_free":
        return {"code": 409, "message": "该报名已免缴费"}

    # 计算费用
    all_event_names = _extract_event_names(reg)
    events = await event_repo.list_events()
    events_map = {e["name"]: _normalize_fee_to_fen(e.get("fee", 0)) for e in events}
    required_fee = _normalize_fee_to_fen(events_map.get(reg.get("required_event", ""), 0))
    fallback_fee = required_fee if required_fee > 0 else 0
    total_fee = sum(
        _normalize_fee_to_fen(events_map.get(n, 0)) or fallback_fee
        for n in all_event_names
    )

    if total_fee <= 0:
        # 免费，直接标记已缴费
        await registration_repo.update_registration(
            registration_id,
            {"payment_status": "paid", "payment_time": int(time.time() * 1000)},
        )
        return {"code": 200, "message": "该项目免费，已自动完成", "data": {"free": True}}

    # TODO: 第二阶段实现真实微信支付
    # 当前返回模拟支付模式
    return {
        "code": 200,
        "message": "使用模拟支付",
        "data": {
            "mock": True,
            "registration_id": registration_id,
            "total_fee": total_fee,
            "event_name": reg.get("event_name", ""),
        },
    }


async def mock_pay(openid: str, registration_id: str) -> dict:
    """模拟支付（仅开发测试环境）"""
    if not settings.ENABLE_MOCK_PAY:
        return {"code": 403, "message": "生产环境不允许模拟支付"}

    reg = await registration_repo.find_by_id(registration_id)
    if not reg:
        return {"code": 404, "message": "报名记录不存在"}
    if reg.get("openid") != openid:
        return {"code": 403, "message": "无权操作此报名记录"}
    if reg.get("payment_status") in ("paid", "admin_free"):
        return {"code": 409, "message": "该报名已缴费"}

    now = int(time.time() * 1000)
    order_no = f"MOCK{int(time.time())}{registration_id[-4:]}"

    await registration_repo.update_registration(
        registration_id,
        {
            "payment_status": "paid",
            "payment_time": now,
            "payment_order_no": order_no,
        },
    )

    return {
        "code": 200,
        "message": "模拟支付成功",
        "data": {
            "payment_status": "paid",
            "payment_time": now,
            "payment_order_no": order_no,
        },
    }


async def query_order(openid: str, registration_id: str) -> dict:
    """查询订单状态"""
    reg = await registration_repo.find_by_id(registration_id)
    if not reg:
        return {"code": 404, "message": "报名记录不存在"}
    if reg.get("openid") != openid:
        return {"code": 403, "message": "无权查询此订单"}

    return {
        "code": 200,
        "data": {
            "payment_status": reg.get("payment_status", "unpaid"),
            "payment_time": reg.get("payment_time"),
            "payment_order_no": reg.get("payment_order_no", ""),
        },
    }
