"""
赛事项目 & 计数器数据访问层
"""
import time
from typing import Optional, List
from bson import ObjectId
from app.database import get_collection

EVENT_COLLECTION = "sign_events"
COUNTER_COLLECTION = "sign_counters"


# ========== 赛事项目 ==========

async def list_events() -> List[dict]:
    """获取所有项目，按 sort_order 排序"""
    col = get_collection(EVENT_COLLECTION)
    cursor = col.find().sort("sort_order", 1)
    return await cursor.to_list(length=200)


async def find_event_by_id(event_id: str) -> Optional[dict]:
    """根据 ID 查找项目"""
    col = get_collection(EVENT_COLLECTION)
    return await col.find_one({"_id": ObjectId(event_id)})


async def create_event(doc: dict) -> str:
    """创建项目"""
    col = get_collection(EVENT_COLLECTION)
    doc["create_time"] = int(time.time() * 1000)
    result = await col.insert_one(doc)
    return str(result.inserted_id)


async def update_event(event_id: str, update_data: dict) -> None:
    """更新项目"""
    col = get_collection(EVENT_COLLECTION)
    update_data["update_time"] = int(time.time() * 1000)
    await col.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})


async def delete_event(event_id: str) -> None:
    """删除项目"""
    col = get_collection(EVENT_COLLECTION)
    await col.delete_one({"_id": ObjectId(event_id)})


# ========== 计数器（准考证号生成） ==========

async def get_next_seq(counter_key: str) -> int:
    """
    原子递增计数器，返回新序号
    使用 find_one_and_update 的 upsert 确保线程安全
    """
    col = get_collection(COUNTER_COLLECTION)
    result = await col.find_one_and_update(
        {"key": counter_key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]
