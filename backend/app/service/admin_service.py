"""
管理员业务逻辑
- 报名查询/统计/详情
- 手动报名
- 项目管理 CRUD
- 图片管理 CRUD
- 设置管理
- 学校管理
- 成绩管理
"""
import logging
import re
import time
from datetime import datetime
from typing import List

from bson import ObjectId
from app.database import get_collection
from app.repository import (
    registration_repo,
    event_repo,
    score_repo,
    image_repo,
    setting_repo,
)
from app.utils.crypto import encrypt_id_card, decrypt_id_card, hash_id_card, mask_id_card
from app.utils.validators import validate_id_card, validate_phone

logger = logging.getLogger(__name__)


def _normalize_event_items(input_val) -> List[str]:
    if isinstance(input_val, list):
        return [str(i).strip() for i in input_val if str(i).strip()]
    if isinstance(input_val, str):
        text = input_val.strip()
        if not text:
            return []
        return [s.strip() for s in re.split(r"[、,，;；\s]+", text) if s.strip()]
    return []


def _extract_registration_items(item: dict) -> List[str]:
    merged = (
        _normalize_event_items(item.get("required_event"))
        + _normalize_event_items(item.get("optional_events"))
        + _normalize_event_items(item.get("event_name"))
    )
    return list(dict.fromkeys(merged))


def _format_registration(item: dict, show_full_id: bool = True) -> dict:
    """格式化报名记录（管理员视角）"""
    decrypted = decrypt_id_card(item.get("id_card", "")) if item.get("id_card") else ""
    id_display = decrypted if show_full_id else mask_id_card(decrypted)

    return {
        "_id": str(item["_id"]),
        "ticket_no": item.get("ticket_no", ""),
        "name": item.get("name", ""),
        "gender": item.get("gender", ""),
        "clothes_size": item.get("clothes_size", ""),
        "school": item.get("school", ""),
        "phone": item.get("phone", ""),
        "id_card": id_display,
        "event_name": item.get("event_name", ""),
        "required_event": item.get("required_event", ""),
        "optional_events": item.get("optional_events", []),
        "is_sports_talent": bool(item.get("is_sports_talent")),
        "payment_status": item.get("payment_status", "unpaid"),
        "payment_order_no": item.get("payment_order_no", ""),
        "payment_time": item.get("payment_time"),
        "registered_by": item.get("registered_by", "self"),
        "create_time": item.get("create_time"),
        "personal_promise_signature": item.get("personal_promise_signature", ""),
        "health_promise_signature": item.get("health_promise_signature", ""),
        "personal_guardian_signature": item.get("personal_guardian_signature", ""),
        "health_guardian_signature": item.get("health_guardian_signature", ""),
    }


# ========== 报名查询 ==========

async def search_registration(keyword: str = "", event_item: str = "", page: int = 1, page_size: int = 20) -> dict:
    """搜索报名记录"""
    if event_item and event_item.strip():
        # 按项目筛选（需全量加载后内存过滤）
        all_rows = await registration_repo.find_all_fields({})
        matched = [
            r for r in all_rows
            if event_item.strip() in _extract_registration_items(r)
        ]
        matched.sort(key=lambda x: x.get("create_time", 0), reverse=True)
        return {
            "code": 200,
            "data": {
                "list": [_format_registration(r) for r in matched],
                "total": len(matched),
                "page": 1,
                "page_size": page_size,
            },
        }

    if not keyword or not keyword.strip():
        total = await registration_repo.count_all()
        items = await registration_repo.find_paginated(page, page_size)
        return {
            "code": 200,
            "data": {
                "list": [_format_registration(r) for r in items],
                "total": total,
                "page": page,
                "page_size": page_size,
            },
        }

    results = await registration_repo.search_by_keyword(keyword.strip())
    return {
        "code": 200,
        "data": {
            "list": [_format_registration(r) for r in results],
            "total": len(results),
            "page": 1,
            "page_size": page_size,
        },
    }


async def get_registration_detail(registration_id: str) -> dict:
    """获取报名详情"""
    reg = await registration_repo.find_by_id(registration_id)
    if not reg:
        return {"code": 404, "message": "报名记录不存在"}
    return {"code": 200, "data": _format_registration(reg)}


async def get_registration_stats() -> dict:
    """获取报名统计"""
    all_rows = await registration_repo.find_all_fields({})
    total = len(all_rows)
    paid = sum(1 for r in all_rows if r.get("payment_status") == "paid")
    admin_free = sum(1 for r in all_rows if r.get("payment_status") == "admin_free")
    unpaid = sum(1 for r in all_rows if r.get("payment_status") in (None, "unpaid", ""))

    # 各项目统计
    events = await event_repo.list_events()
    item_count = {}
    for row in all_rows:
        for name in _extract_registration_items(row):
            item_count[name] = item_count.get(name, 0) + 1

    event_stats = []
    covered = set()
    for evt in events:
        ename = evt.get("name", "")
        event_stats.append({
            "key": str(evt["_id"]),
            "event_id": str(evt["_id"]),
            "event_name": ename,
            "count": item_count.get(ename, 0),
        })
        covered.add(ename)

    for name, count in item_count.items():
        if count > 0 and name not in covered:
            event_stats.append({
                "key": f"name_{name}",
                "event_id": "",
                "event_name": name,
                "count": count,
            })

    unpaid_list = [
        {
            "_id": str(r["_id"]),
            "ticket_no": r.get("ticket_no", "-"),
            "name": r.get("name", "-"),
            "phone": r.get("phone", "-"),
            "school": r.get("school", "-"),
            "event_name": r.get("event_name", "-"),
            "create_time": r.get("create_time"),
            "payment_status": r.get("payment_status", "unpaid"),
        }
        for r in sorted(all_rows, key=lambda x: x.get("create_time", 0), reverse=True)
        if r.get("payment_status") in (None, "unpaid", "")
    ][:200]

    return {
        "code": 200,
        "data": {
            "total": total,
            "paid": paid,
            "unpaid": unpaid,
            "adminFree": admin_free,
            "eventStats": event_stats,
            "unpaidList": unpaid_list,
        },
    }


# ========== 手动报名 ==========

async def manual_register(admin_user_id: str, data: dict) -> dict:
    """管理员手动报名"""
    name = (data.get("name") or "").strip()
    gender = data.get("gender", "")
    school = (data.get("school") or "").strip()
    phone = (data.get("phone") or "").strip()
    id_card = (data.get("id_card") or "").strip().upper()
    required_event = (data.get("required_event") or "").strip()
    optional_events = data.get("optional_events") or []

    if not name:
        return {"code": 400, "message": "请输入姓名"}
    if gender not in ("male", "female"):
        return {"code": 400, "message": "请选择性别"}
    if not school:
        return {"code": 400, "message": "请输入学校"}
    if not phone or len(phone) != 11 or not validate_phone(phone):
        return {"code": 400, "message": "请输入正确的11位手机号"}
    if not id_card or len(id_card) != 18 or not validate_id_card(id_card):
        return {"code": 400, "message": "请输入正确的18位身份证号"}
    if not required_event:
        return {"code": 400, "message": "缺少必考项目"}
    if not optional_events or len(optional_events) < 2:
        return {"code": 400, "message": "选考项目最少选择2项"}

    id_card_hash_val = hash_id_card(id_card)
    existing = await registration_repo.find_by_id_card_hash(id_card_hash_val)
    if existing:
        return {"code": 409, "message": "该身份证号已报名，请勿重复报名"}

    required_code = "01" if gender == "male" else "02"
    year = str(datetime.now().year)
    seq = await event_repo.get_next_seq(f"ticket_{required_code}")
    ticket_no = f"{year}{required_code}{str(seq).zfill(4)}"

    registration = {
        "openid": "",
        "ticket_no": ticket_no,
        "name": name,
        "gender": gender,
        "clothes_size": (data.get("clothes_size") or "").strip(),
        "school": school,
        "phone": phone,
        "id_card": encrypt_id_card(id_card),
        "id_card_hash": id_card_hash_val,
        "required_event": required_event,
        "optional_events": optional_events,
        "event_name": data.get("event_name") or required_event,
        "is_sports_talent": bool(data.get("is_sports_talent")),
        "payment_status": "admin_free",
        "payment_order_no": "",
        "payment_time": None,
        "registered_by": "admin",
        "admin_id": admin_user_id,
    }

    reg_id = await registration_repo.create_registration(registration)
    return {
        "code": 200,
        "message": "手动报名成功",
        "data": {
            "_id": reg_id,
            "ticket_no": ticket_no,
            "name": name,
            "payment_status": "admin_free",
        },
    }


# ========== 项目管理 ==========

async def list_events() -> dict:
    items = await event_repo.list_events()
    return {"code": 200, "data": [{**e, "_id": str(e["_id"])} for e in items]}


async def add_event(data: dict) -> dict:
    name = (data.get("name") or "").strip()
    if not name:
        return {"code": 400, "message": "请输入项目名称"}

    doc = {
        "name": name,
        "fee": int(data.get("fee", 0)),
        "code": data.get("code", "00"),
        "status": "active",
        "sort_order": int(data.get("sort_order", 0)),
        "is_required": bool(data.get("is_required")),
    }
    eid = await event_repo.create_event(doc)
    return {"code": 200, "message": "添加成功", "data": {"_id": eid, **doc}}


async def update_event(event_id: str, data: dict) -> dict:
    if not event_id:
        return {"code": 400, "message": "缺少项目ID"}
    update = {}
    if data.get("name") is not None:
        update["name"] = data["name"].strip()
    if data.get("fee") is not None:
        update["fee"] = int(data["fee"])
    if data.get("code") is not None:
        update["code"] = data["code"]
    if data.get("status") is not None:
        update["status"] = data["status"]
    if data.get("sort_order") is not None:
        update["sort_order"] = int(data["sort_order"])
    await event_repo.update_event(event_id, update)
    return {"code": 200, "message": "更新成功"}


async def delete_event(event_id: str) -> dict:
    if not event_id:
        return {"code": 400, "message": "缺少项目ID"}
    evt = await event_repo.find_event_by_id(event_id)
    if evt and evt.get("is_required"):
        return {"code": 400, "message": "必考项目不可删除"}
    await event_repo.delete_event(event_id)
    return {"code": 200, "message": "删除成功"}


# ========== 轮播图管理 ==========

async def list_banners(position: str = None) -> dict:
    items = await image_repo.list_banners(position)
    return {"code": 200, "data": [{**b, "_id": str(b["_id"])} for b in items]}


async def add_banner(data: dict) -> dict:
    doc = {
        "image_url": data["image_url"],
        "position": data["position"],
        "sort_order": int(data.get("sort_order", 0)),
        "status": "active",
    }
    bid = await image_repo.create_banner(doc)
    return {"code": 200, "message": "添加成功", "data": {"_id": bid, **doc}}


async def update_banner(banner_id: str, data: dict) -> dict:
    update = {}
    if data.get("image_url") is not None:
        update["image_url"] = data["image_url"]
    if data.get("position") is not None:
        update["position"] = data["position"]
    if data.get("sort_order") is not None:
        update["sort_order"] = int(data["sort_order"])
    if data.get("status") is not None:
        update["status"] = data["status"]
    await image_repo.update_banner(banner_id, update)
    return {"code": 200, "message": "更新成功"}


async def delete_banner(banner_id: str) -> dict:
    await image_repo.delete_banner(banner_id)
    return {"code": 200, "message": "删除成功"}


# ========== 赛事图片管理 ==========

async def list_event_images() -> dict:
    items = await image_repo.list_event_images()
    return {"code": 200, "data": [{**i, "_id": str(i["_id"])} for i in items]}


async def add_event_image(data: dict) -> dict:
    doc = {"image_url": data["image_url"], "sort_order": int(data.get("sort_order", 0)), "status": "active"}
    iid = await image_repo.create_event_image(doc)
    return {"code": 200, "message": "添加成功", "data": {"_id": iid, **doc}}


async def update_event_image(image_id: str, data: dict) -> dict:
    update = {}
    if data.get("sort_order") is not None:
        update["sort_order"] = int(data["sort_order"])
    if data.get("status") is not None:
        update["status"] = data["status"]
    await image_repo.update_event_image(image_id, update)
    return {"code": 200, "message": "更新成功"}


async def delete_event_image(image_id: str) -> dict:
    await image_repo.delete_event_image(image_id)
    return {"code": 200, "message": "删除成功"}


# ========== 须知图片管理 ==========

async def list_notice_images() -> dict:
    items = await image_repo.list_notice_images()
    return {"code": 200, "data": [{**i, "_id": str(i["_id"])} for i in items]}


async def add_notice_image(data: dict) -> dict:
    doc = {"image_url": data["image_url"], "sort_order": int(data.get("sort_order", 0)), "status": "active"}
    iid = await image_repo.create_notice_image(doc)
    return {"code": 200, "message": "添加成功", "data": {"_id": iid, **doc}}


async def update_notice_image(image_id: str, data: dict) -> dict:
    update = {}
    if data.get("sort_order") is not None:
        update["sort_order"] = int(data["sort_order"])
    if data.get("status") is not None:
        update["status"] = data["status"]
    await image_repo.update_notice_image(image_id, update)
    return {"code": 200, "message": "更新成功"}


async def delete_notice_image(image_id: str) -> dict:
    await image_repo.delete_notice_image(image_id)
    return {"code": 200, "message": "删除成功"}


async def reorder_notice_images(ordered_ids: list) -> dict:
    await image_repo.reorder_notice_images(ordered_ids)
    return {"code": 200, "message": "排序更新成功"}


# ========== 设置管理 ==========

async def get_settings() -> dict:
    data = await setting_repo.get_all_settings()
    return {"code": 200, "data": data}


async def update_settings(settings_dict: dict) -> dict:
    for key, value in settings_dict.items():
        await setting_repo.upsert_setting(key, value)
    return {"code": 200, "message": "保存成功"}


# ========== 学校管理 ==========

async def list_schools() -> dict:
    items = await setting_repo.list_schools()
    return {"code": 200, "data": [{**s, "_id": str(s["_id"])} for s in items]}


async def add_school(name: str, sort_order: int = 0) -> dict:
    name = name.strip()
    if not name:
        return {"code": 400, "message": "学校名称不能为空"}
    existing = await setting_repo.find_school_by_name(name)
    if existing:
        return {"code": 400, "message": "该学校已存在"}
    await setting_repo.create_school(name, sort_order)
    return {"code": 200, "message": "添加成功"}


async def update_school(school_id: str, data: dict) -> dict:
    update = {}
    if data.get("name") is not None:
        update["name"] = data["name"].strip()
    if data.get("sort_order") is not None:
        update["sort_order"] = int(data["sort_order"])
    if data.get("status") is not None:
        update["status"] = data["status"]
    await setting_repo.update_school(school_id, update)
    return {"code": 200, "message": "更新成功"}


async def delete_school(school_id: str) -> dict:
    await setting_repo.delete_school(school_id)
    return {"code": 200, "message": "删除成功"}


# ========== 成绩管理 ==========

async def import_scores(scores_data: list) -> dict:
    if len(scores_data) > 5000:
        return {"code": 400, "message": "单次导入不能超过5000条"}

    success_count = 0
    fail_count = 0
    fail_details = []

    for i, item in enumerate(scores_data):
        ticket_no = str(item.get("ticket_no", "")).strip()
        name = str(item.get("name", "")).strip()
        event_name = str(item.get("event_name", "")).strip()

        if not ticket_no or not name or not event_name:
            fail_count += 1
            fail_details.append({"row": i + 1, "ticket_no": ticket_no, "reason": "缺少必填字段"})
            continue

        reg = await registration_repo.find_by_ticket_no(ticket_no)
        if not reg:
            fail_count += 1
            fail_details.append({"row": i + 1, "ticket_no": ticket_no, "reason": "证书编号不存在"})
            continue

        score_data = {
            "ticket_no": ticket_no,
            "name": name,
            "school": reg.get("school", ""),
            "gender": reg.get("gender", ""),
            "event_name": event_name,
            "score": str(item.get("score", "")),
            "points": str(item.get("points", "")),
            "remark": str(item.get("remark", "")),
        }
        await score_repo.upsert_score(ticket_no, event_name, score_data)
        success_count += 1

    return {
        "code": 200,
        "message": f"导入完成：成功 {success_count} 条，失败 {fail_count} 条",
        "data": {"success_count": success_count, "fail_count": fail_count, "fail_details": fail_details},
    }


async def clear_scores() -> dict:
    removed = await score_repo.clear_all()
    return {"code": 200, "message": f"已清空 {removed} 条成绩数据", "data": {"removed": removed}}


async def list_scores(page: int = 1, page_size: int = 20, keyword: str = "") -> dict:
    """列出成绩（按报名记录分组展示）"""
    regs = await registration_repo.find_by_payment_status(["paid", "admin_free"])

    # 关键词过滤
    if keyword:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        regs = [r for r in regs if pattern.search(r.get("ticket_no", "")) or pattern.search(r.get("name", ""))]

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
        })

    # 只显示有成绩的
    regs_with_score = [r for r in regs if str(r.get("ticket_no", "")).strip() in score_map]
    total = len(regs_with_score)
    start = (page - 1) * page_size
    page_regs = regs_with_score[start:start + page_size]

    result_list = []
    for reg in page_regs:
        tn = str(reg.get("ticket_no", "")).strip()
        reg_events = _extract_registration_items(reg)[:3]
        student_scores = score_map.get(tn, [])

        event_slots = []
        for idx in range(3):
            ename = reg_events[idx] if idx < len(reg_events) else ""
            matched = next((s for s in student_scores if s["event_name"] == ename), None) if ename else None
            event_slots.append({
                "event_name": ename,
                "score": matched["score"] if matched else "",
                "points": matched["points"] if matched else "",
            })

        gender_text = "男" if reg.get("gender") == "male" else ("女" if reg.get("gender") == "female" else "")
        result_list.append({
            "_id": str(reg["_id"]),
            "ticket_no": reg.get("ticket_no", ""),
            "name": reg.get("name", ""),
            "school": reg.get("school", ""),
            "gender": reg.get("gender", ""),
            "gender_text": gender_text,
            "phone": reg.get("phone", ""),
            "is_sports_talent": bool(reg.get("is_sports_talent")),
            "event_slots": event_slots,
        })

    return {"code": 200, "data": {"list": result_list, "total": total, "page": page, "page_size": page_size}}


async def export_students() -> dict:
    """导出学生数据"""
    regs = await registration_repo.find_by_payment_status(["paid", "admin_free"])
    if not regs:
        return {"code": 200, "message": "暂无已缴费学生", "data": {"headers": [], "rows": [], "total": 0}}

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
        })

    headers = ["证书编号", "姓名", "学校", "性别", "手机号", "体育特长生",
               "一类项目", "成绩", "分数", "二类项目", "成绩", "分数", "三类项目", "成绩", "分数"]

    rows = []
    for reg in regs:
        gender = "男" if reg.get("gender") == "male" else ("女" if reg.get("gender") == "female" else "")
        tn = str(reg.get("ticket_no", "")).strip()
        student_scores = score_map.get(tn, [])
        reg_events = _extract_registration_items(reg)[:3]

        slots = []
        for idx in range(3):
            ename = reg_events[idx] if idx < len(reg_events) else ""
            matched = next((s for s in student_scores if s["event_name"] == ename), None) if ename else None
            slots.append({
                "event_name": ename,
                "score": matched["score"] if matched else "",
                "points": matched["points"] if matched else "",
            })

        rows.append([
            reg.get("ticket_no", ""), reg.get("name", ""), reg.get("school", ""),
            gender, reg.get("phone", ""), "是" if reg.get("is_sports_talent") else "否",
            slots[0]["event_name"], slots[0]["score"], slots[0]["points"],
            slots[1]["event_name"], slots[1]["score"], slots[1]["points"],
            slots[2]["event_name"], slots[2]["score"], slots[2]["points"],
        ])

    return {"code": 200, "data": {"headers": headers, "rows": rows, "total": len(regs)}}


# ========== 赛事 (Competition) 管理 ==========

async def list_competitions():
    """获取所有赛事列表"""
    col = get_collection("sign_competitions")
    cursor = col.find({"status": {"$ne": "deleted"}}).sort("create_time", -1)
    items = await cursor.to_list(length=100)
    for item in items:
        item["_id"] = str(item["_id"])
    return {"code": 200, "data": items}


async def add_competition(data: dict):
    """新增赛事"""
    col = get_collection("sign_competitions")
    data["create_time"] = int(time.time() * 1000)
    data["status"] = "active"
    result = await col.insert_one(data)
    return {"code": 200, "message": "赛事创建成功", "data": {"id": str(result.inserted_id)}}


async def update_competition(comp_id: str, data: dict):
    """编辑赛事信息"""
    col = get_collection("sign_competitions")
    if not comp_id:
        return {"code": 400, "message": "缺少赛事ID"}
    await col.update_one({"_id": ObjectId(comp_id)}, {"$set": data})
    return {"code": 200, "message": "赛事信息已更新"}


async def delete_competition(comp_id: str):
    """删除赛事 (软删除)"""
    col = get_collection("sign_competitions")
    if not comp_id:
        return {"code": 400, "message": "缺少赛事ID"}
    await col.update_one({"_id": ObjectId(comp_id)}, {"$set": {"status": "deleted"}})
    return {"code": 200, "message": "赛事已成功移除"}

async def get_competition_leaderboard(comp_id: str) -> dict:
    """计算赛事排行榜"""
    col_comp = get_collection("sign_competitions")
    comp = await col_comp.find_one({"_id": ObjectId(comp_id)})
    if not comp:
        return {"code": 404, "message": "赛事不存在"}
    
    comp_type = comp.get("comp_type", "general")
    
    # 获取该赛事的所有成绩
    # 假设成绩是通过 ticket_no 关联的，我们需要先找到所有报名的准考证号
    regs = await registration_repo.find_all_fields({})
    ticket_nos = [r["ticket_no"] for r in regs if r.get("ticket_no")]
    scores = await score_repo.find_by_ticket_nos(ticket_nos)
    
    # 按人分组汇总成绩
    user_results = {}
    for s in scores:
        tn = s["ticket_no"]
        if tn not in user_results:
            user_results[tn] = {
                "name": s["name"],
                "school": s.get("school", ""),
                "ticket_no": tn,
                "finished_count": 0,
                "total_time_ms": 0,
                "best_time_ms": 999999999,
                "events": []
            }
        user_results[tn]["finished_count"] += 1
        user_results[tn]["total_time_ms"] += s.get("time_ms", 0)
        if s.get("time_ms", 0) < user_results[tn]["best_time_ms"]:
            user_results[tn]["best_time_ms"] = s["time_ms"]
        user_results[tn]["events"].append(s)

    leaderboard = list(user_results.values())

    if comp_type == "bouldering":
        # 抱石赛排序：完攀线路数降序 -> 总用时升序
        leaderboard.sort(key=lambda x: (-x["finished_count"], x["total_time_ms"]))
    elif comp_type == "speed":
        # 速度赛排序：最佳用时升序
        leaderboard.sort(key=lambda x: x["best_time_ms"])
    else:
        # 普通排序：完攀数降序
        leaderboard.sort(key=lambda x: -x["finished_count"])

    # 截取前 50 名
    return {"code": 200, "data": leaderboard[:50]}

