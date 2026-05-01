"""
报名业务逻辑
- 提交报名（参数校验、防重复、生成准考证号、加密身份证）
- 查询我的报名记录
- 准考证信息
- 成绩查询
"""
import logging
import time
from datetime import datetime
from typing import List

from app.repository import registration_repo, event_repo, score_repo, setting_repo, image_repo
from app.utils.crypto import encrypt_id_card, decrypt_id_card, hash_id_card, mask_id_card
from app.utils.validators import validate_id_card, validate_phone
from app.utils.i18n import t

logger = logging.getLogger(__name__)


def _normalize_event_list(input_val) -> List[str]:
    """将项目输入规范化为字符串列表"""
    if isinstance(input_val, list):
        return [str(item).strip() for item in input_val if str(item).strip()]
    if isinstance(input_val, str):
        import re
        return [s.strip() for s in re.split(r"[、,，;；\s]+", input_val) if s.strip()]
    return []


def _normalize_fee_to_fen(fee_raw) -> int:
    """将费用规范化为分"""
    try:
        num = float(fee_raw)
        if num <= 0:
            return 0
        if num == int(num):
            return int(num)
        return round(num * 100)
    except (TypeError, ValueError):
        return 0


async def _generate_ticket_no(event_code: str) -> str:
    """
    生成准考证号：年份(4位) + 项目编号(2位) + 流水号(4位)
    使用原子递增保证并发安全
    """
    year = str(datetime.now().year)
    counter_key = f"ticket_{event_code}"
    seq = await event_repo.get_next_seq(counter_key)
    return f"{year}{event_code}{str(seq).zfill(4)}"


async def submit_registration(openid: str, data: dict) -> dict:
    """提交报名"""
    # 参数校验
    name = (data.get("name") or "").strip()
    gender = data.get("gender", "")
    school = (data.get("school") or "").strip()
    phone = (data.get("phone") or "").strip()
    id_card = (data.get("id_card") or "").strip().upper()
    required_event = (data.get("required_event") or "").strip()
    optional_events = data.get("optional_events") or []

    if not name:
        return {"code": 400, "message": t("error_input_invalid")}
    if gender not in ("male", "female"):
        return {"code": 400, "message": t("error_input_invalid")}
    if not school:
        return {"code": 400, "message": t("error_input_invalid")}
    if not phone or len(phone) != 11 or not validate_phone(phone):
        return {"code": 400, "message": t("error_phone")}
    if not id_card or len(id_card) != 18 or not validate_id_card(id_card):
        return {"code": 400, "message": t("error_id_card")}
    if not required_event:
        return {"code": 400, "message": t("error_input_invalid")}
    if not optional_events or len(optional_events) < 2:
        return {"code": 400, "message": t("error_input_invalid")}
    if not data.get("personal_promise_signature") or not data.get("health_promise_signature"):
        return {"code": 400, "message": t("error_input_invalid")}
    if not data.get("personal_guardian_signature") or not data.get("health_guardian_signature"):
        return {"code": 400, "message": t("error_input_invalid")}

    # 防重复报名
    id_card_hash_val = hash_id_card(id_card)
    existing = await registration_repo.find_by_id_card_hash(id_card_hash_val)
    if existing:
        return {"code": 409, "message": t("error_duplicate")}

    # 生成准考证号
    required_code = "01" if gender == "male" else "02"
    ticket_no = await _generate_ticket_no(required_code)

    # 加密身份证号
    encrypted_id = encrypt_id_card(id_card)

    event_name = data.get("event_name") or required_event

    registration = {
        "openid": openid,
        "ticket_no": ticket_no,
        "name": name,
        "gender": gender,
        "clothes_size": (data.get("clothes_size") or "").strip(),
        "school": school,
        "phone": phone,
        "id_card": encrypted_id,
        "avatar_url": (data.get("avatar_url") or "").strip(),
        "id_card_hash": id_card_hash_val,
        "required_event": required_event,
        "optional_events": optional_events,
        "event_name": event_name,
        "is_sports_talent": bool(data.get("is_sports_talent")),
        "personal_promise_signature": (data.get("personal_promise_signature") or "").strip(),
        "health_promise_signature": (data.get("health_promise_signature") or "").strip(),
        "personal_guardian_signature": (data.get("personal_guardian_signature") or "").strip(),
        "health_guardian_signature": (data.get("health_guardian_signature") or "").strip(),
        "payment_status": "unpaid",
        "payment_order_no": "",
        "payment_time": None,
        "registered_by": "self",
        "admin_id": "",
    }

    reg_id = await registration_repo.create_registration(registration)

    return {
        "code": 200,
        "message": t("register_success"),
        "data": {
            "_id": reg_id,
            "ticket_no": ticket_no,
            "name": name,
            "gender": gender,
            "school": school,
            "phone": phone,
            "id_card_masked": mask_id_card(id_card),
            "required_event": required_event,
            "optional_events": optional_events,
            "event_name": event_name,
            "payment_status": "unpaid",
        },
    }


async def update_avatar(openid: str, ticket_no: str, avatar_url: str) -> dict:
    """更新报名头像"""
    reg = await registration_repo.find_by_ticket_no(ticket_no)
    if not reg:
        return {"code": 404, "message": t("record_not_found")}
    if reg["openid"] != openid:
        return {"code": 403, "message": t("error_no_permission")}

    await registration_repo.update_registration(
        str(reg["_id"]), {"avatar_url": avatar_url.strip()}
    )
    return {"code": 200, "message": t("success")}


async def check_duplicate(id_card: str) -> dict:
    """检查重复报名"""
    id_card_hash_val = hash_id_card(id_card)
    existing = await registration_repo.find_by_id_card_hash(id_card_hash_val)

    if existing:
        return {
            "code": 200,
            "data": {
                "is_duplicate": True,
                "registration": {
                    "_id": str(existing["_id"]),
                    "ticket_no": existing.get("ticket_no", ""),
                    "event_name": existing.get("event_name", ""),
                    "payment_status": existing.get("payment_status", ""),
                },
            },
        }
    return {"code": 200, "data": {"is_duplicate": False, "registration": None}}


async def get_my_registrations(openid: str) -> dict:
    """获取当前用户所有报名记录"""
    regs = await registration_repo.find_by_openid(openid)

    # 查询所有项目费用
    events = await event_repo.list_events()
    events_map = {e["name"]: _normalize_fee_to_fen(e.get("fee", 0)) for e in events}

    result_list = []
    for item in regs:
        required = (item.get("required_event") or "").strip()
        optional = _normalize_event_list(item.get("optional_events"))
        from_event = _normalize_event_list(item.get("event_name"))
        all_names = list(dict.fromkeys([required] + optional + from_event))
        all_names = [n for n in all_names if n]

        required_fee = _normalize_fee_to_fen(events_map.get(required, 0))
        fallback_fee = required_fee if required_fee > 0 else 0
        fee = sum(
            _normalize_fee_to_fen(events_map.get(n, 0)) or fallback_fee
            for n in all_names
        )

        decrypted_id = decrypt_id_card(item.get("id_card", "")) if item.get("id_card") else ""

        result_list.append({
            "_id": str(item["_id"]),
            "ticket_no": item.get("ticket_no", ""),
            "name": item.get("name", ""),
            "gender": item.get("gender", ""),
            "clothes_size": item.get("clothes_size", ""),
            "school": item.get("school", ""),
            "phone": item.get("phone", ""),
            "avatar_url": item.get("avatar_url", ""),
            "id_card_masked": mask_id_card(decrypted_id) if decrypted_id else "",
            "required_event": item.get("required_event", ""),
            "optional_events": item.get("optional_events", []),
            "event_name": item.get("event_name", ""),
            "payment_status": item.get("payment_status", "unpaid"),
            "registered_by": item.get("registered_by", "self"),
            "create_time": item.get("create_time"),
            "fee": fee,
        })

    return {"code": 200, "data": result_list}


async def get_ticket(ticket_no: str, openid: str = None) -> dict:
    """获取准考证信息"""
    reg = await registration_repo.find_by_ticket_no(ticket_no)
    if not reg:
        return {"code": 404, "message": t("record_not_found")}

    is_self = openid and reg.get("openid") == openid
    decrypted_id = decrypt_id_card(reg.get("id_card", "")) if reg.get("id_card") else ""

    return {
        "code": 200,
        "data": {
            "_id": str(reg["_id"]),
            "ticket_no": reg.get("ticket_no", ""),
            "name": reg.get("name", ""),
            "gender": reg.get("gender", ""),
            "clothes_size": reg.get("clothes_size", ""),
            "school": reg.get("school", ""),
            "phone": reg.get("phone", ""),
            "avatar_url": reg.get("avatar_url", ""),
            "id_card_masked": mask_id_card(decrypted_id) if decrypted_id else "",
            "required_event": reg.get("required_event", ""),
            "optional_events": reg.get("optional_events", []),
            "event_name": reg.get("event_name", ""),
            "is_sports_talent": bool(reg.get("is_sports_talent")),
            "payment_status": reg.get("payment_status", ""),
            "payment_order_no": reg.get("payment_order_no", "") if is_self else "",
            "create_time": reg.get("create_time"),
        },
    }


async def get_settings() -> dict:
    """获取前端可用设置"""
    keys = [
        "event_title", "event_location", "event_date",
        "personal_promise_text", "health_promise_text",
        "personal_promise_image", "health_promise_image",
        "registration_deadline",
    ]
    settings_map = await setting_repo.get_settings_by_keys(keys)
    return {
        "code": 200,
        "data": settings_map,
        "server_time": int(time.time() * 1000)
    }


async def list_notice_images() -> dict:
    """获取参赛须知图片"""
    images = await image_repo.list_active_notice_images()
    return {
        "code": 200,
        "data": [
            {**img, "_id": str(img["_id"])} for img in images
        ],
    }


async def get_my_scores(openid: str) -> dict:
    """查询当前用户所有报名人员的成绩"""
    regs = await registration_repo.find_by_openid(openid)
    if not regs:
        return {"code": 200, "data": {"items": []}}

    ticket_nos = [str(r.get("ticket_no", "")).strip() for r in regs if r.get("ticket_no")]
    all_scores = await score_repo.find_by_ticket_nos(ticket_nos) if ticket_nos else []

    score_map = {}
    for s in all_scores:
        tn = str(s.get("ticket_no", "")).strip()
        if tn not in score_map:
            score_map[tn] = []
        score_map[tn].append({
            "event_name": s.get("event_name", ""),
            "score": s.get("score", ""),
            "points": s.get("points", ""),
            "remark": s.get("remark", ""),
        })

    items = []
    for reg in regs:
        tn = str(reg.get("ticket_no", "")).strip()
        event_scores = sorted(
            score_map.get(tn, []), key=lambda x: x.get("event_name", "")
        )
        items.append({
            "_id": str(reg["_id"]),
            "ticket_no": reg.get("ticket_no", ""),
            "name": reg.get("name", ""),
            "gender": reg.get("gender", ""),
            "phone": reg.get("phone", ""),
            "event_name": reg.get("event_name", ""),
            "event_scores": event_scores,
        })

    return {"code": 200, "data": {"items": items}}


async def get_scores_by_ticket_no(ticket_no: str) -> dict:
    """按准考证号查询成绩"""
    reg = await registration_repo.find_by_ticket_no(ticket_no)
    if not reg:
        return {"code": 404, "message": t("record_not_found")}

    scores = await score_repo.find_by_ticket_no(ticket_no)
    event_scores = [
        {
            "event_name": s.get("event_name", ""),
            "score": s.get("score", ""),
            "points": s.get("points", ""),
            "remark": s.get("remark", ""),
        }
        for s in scores
    ]

    return {
        "code": 200,
        "data": {
            "item": {
                "_id": str(reg["_id"]),
                "ticket_no": reg.get("ticket_no", ticket_no),
                "name": reg.get("name", ""),
                "gender": reg.get("gender", ""),
                "phone": reg.get("phone", ""),
                "event_name": reg.get("event_name", ""),
                "event_scores": event_scores,
            }
        },
    }
