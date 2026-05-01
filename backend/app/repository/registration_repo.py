"""
报名记录数据访问层
"""
import time
import re
from typing import Optional, List
from bson import ObjectId
from app.database import get_collection

COLLECTION = "sign_registrations"


async def find_by_id(registration_id: str) -> Optional[dict]:
    """根据 ID 查找报名记录"""
    col = get_collection(COLLECTION)
    return await col.find_one({"_id": ObjectId(registration_id)})


async def find_by_ticket_no(ticket_no: str) -> Optional[dict]:
    """根据准考证号查找"""
    col = get_collection(COLLECTION)
    return await col.find_one({"ticket_no": ticket_no})


async def find_by_id_card_hash(id_card_hash: str) -> Optional[dict]:
    """根据身份证哈希查找（判重）"""
    col = get_collection(COLLECTION)
    return await col.find_one({"id_card_hash": id_card_hash})


async def find_by_openid(openid: str) -> List[dict]:
    """获取用户所有报名记录"""
    col = get_collection(COLLECTION)
    cursor = col.find({"openid": openid}).sort("create_time", -1)
    return await cursor.to_list(length=1000)


async def create_registration(doc: dict) -> str:
    """创建报名记录，返回 ID"""
    col = get_collection(COLLECTION)
    doc["create_time"] = int(time.time() * 1000)
    doc["update_time"] = int(time.time() * 1000)
    result = await col.insert_one(doc)
    return str(result.inserted_id)


async def update_registration(registration_id: str, update_data: dict) -> None:
    """更新报名记录"""
    col = get_collection(COLLECTION)
    update_data["update_time"] = int(time.time() * 1000)
    await col.update_one(
        {"_id": ObjectId(registration_id)},
        {"$set": update_data},
    )


async def count_all() -> int:
    """总报名数"""
    col = get_collection(COLLECTION)
    return await col.count_documents({})


async def find_paginated(page: int, page_size: int) -> List[dict]:
    """分页查询报名记录"""
    col = get_collection(COLLECTION)
    skip = (page - 1) * page_size
    cursor = col.find().sort("create_time", -1).skip(skip).limit(page_size)
    return await cursor.to_list(length=page_size)


async def search_by_keyword(keyword: str, limit: int = 50) -> List[dict]:
    """
    按关键词搜索：准考证号精确 → 姓名模糊 → 手机号模糊
    """
    col = get_collection(COLLECTION)

    # 1. 准考证号精确匹配
    results = await col.find({"ticket_no": keyword}).to_list(length=limit)
    if results:
        return results

    # 2. 姓名模糊匹配
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    results = await col.find({"name": pattern}).sort("create_time", -1).to_list(length=limit)
    if results:
        return results

    # 3. 手机号匹配
    results = await col.find({"phone": pattern}).to_list(length=limit)
    return results


async def find_all_fields(fields: dict) -> List[dict]:
    """获取所有报名记录的指定字段"""
    col = get_collection(COLLECTION)
    cursor = col.find({}, fields)
    return await cursor.to_list(length=10000)


async def find_by_payment_status(statuses: List[str]) -> List[dict]:
    """按付款状态筛选"""
    col = get_collection(COLLECTION)
    cursor = col.find({"payment_status": {"$in": statuses}}).sort("ticket_no", 1)
    return await cursor.to_list(length=10000)


async def find_by_payment_order_no(order_no: str) -> Optional[dict]:
    """根据支付订单号查找"""
    col = get_collection(COLLECTION)
    return await col.find_one({"payment_order_no": order_no})
