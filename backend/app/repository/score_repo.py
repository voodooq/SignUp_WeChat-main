"""
成绩数据访问层
"""
import time
from typing import Optional, List
from bson import ObjectId
from app.database import get_collection

COLLECTION = "sign_scores"


async def find_by_ticket_and_event(ticket_no: str, event_name: str) -> Optional[dict]:
    """根据准考证号 + 项目名查找成绩"""
    col = get_collection(COLLECTION)
    return await col.find_one({"ticket_no": ticket_no, "event_name": event_name})


async def find_by_ticket_no(ticket_no: str) -> List[dict]:
    """获取某个准考证号的所有成绩"""
    col = get_collection(COLLECTION)
    cursor = col.find({"ticket_no": ticket_no}).sort("event_name", 1)
    return await cursor.to_list(length=100)


async def find_by_ticket_nos(ticket_nos: List[str]) -> List[dict]:
    """批量获取多个准考证号的成绩"""
    col = get_collection(COLLECTION)
    cursor = col.find({"ticket_no": {"$in": ticket_nos}}).sort("event_name", 1)
    return await cursor.to_list(length=10000)


async def upsert_score(ticket_no: str, event_name: str, data: dict) -> None:
    """插入或更新成绩（按 ticket_no + event_name 唯一）"""
    col = get_collection(COLLECTION)
    data["updated_at"] = int(time.time() * 1000)
    await col.update_one(
        {"ticket_no": ticket_no, "event_name": event_name},
        {"$set": data, "$setOnInsert": {"created_at": int(time.time() * 1000)}},
        upsert=True,
    )


async def clear_all() -> int:
    """清空所有成绩，返回删除数量"""
    col = get_collection(COLLECTION)
    result = await col.delete_many({})
    return result.deleted_count


async def count_all() -> int:
    """成绩总数"""
    col = get_collection(COLLECTION)
    return await col.count_documents({})
