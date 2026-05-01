"""
系统设置 & 学校数据访问层
"""
import time
from typing import Optional, List, Dict
from bson import ObjectId
from app.database import get_collection

SETTINGS_COLLECTION = "sign_settings"
SCHOOLS_COLLECTION = "sign_schools"


# ========== 系统设置 ==========

async def get_settings_by_keys(keys: List[str]) -> Dict[str, str]:
    """获取指定 key 的设置值"""
    col = get_collection(SETTINGS_COLLECTION)
    cursor = col.find({"key": {"$in": keys}})
    result = {}
    async for item in cursor:
        result[item["key"]] = item.get("value", "")
    return result


async def get_all_settings() -> Dict[str, dict]:
    """获取所有设置（管理员用，带 _id）"""
    col = get_collection(SETTINGS_COLLECTION)
    cursor = col.find({})
    result = {}
    async for item in cursor:
        result[item["key"]] = {"_id": str(item["_id"]), "value": item.get("value", "")}
    return result


async def upsert_setting(key: str, value: str) -> None:
    """插入或更新配置项"""
    col = get_collection(SETTINGS_COLLECTION)
    await col.update_one(
        {"key": key},
        {
            "$set": {"value": value, "updated_at": int(time.time() * 1000)},
            "$setOnInsert": {"created_at": int(time.time() * 1000)},
        },
        upsert=True,
    )


# ========== 学校管理 ==========

async def list_schools() -> List[dict]:
    """获取所有学校"""
    col = get_collection(SCHOOLS_COLLECTION)
    cursor = col.find().sort([("sort_order", 1), ("created_at", -1)])
    return await cursor.to_list(length=500)


async def find_school_by_name(name: str) -> Optional[dict]:
    """根据名称查找学校"""
    col = get_collection(SCHOOLS_COLLECTION)
    return await col.find_one({"name": name})


async def create_school(name: str, sort_order: int = 0) -> str:
    """创建学校"""
    col = get_collection(SCHOOLS_COLLECTION)
    doc = {
        "name": name,
        "sort_order": sort_order,
        "status": "active",
        "created_at": int(time.time() * 1000),
        "updated_at": int(time.time() * 1000),
    }
    result = await col.insert_one(doc)
    return str(result.inserted_id)


async def update_school(school_id: str, update_data: dict) -> None:
    """更新学校"""
    col = get_collection(SCHOOLS_COLLECTION)
    update_data["updated_at"] = int(time.time() * 1000)
    await col.update_one({"_id": ObjectId(school_id)}, {"$set": update_data})


async def delete_school(school_id: str) -> None:
    """删除学校"""
    col = get_collection(SCHOOLS_COLLECTION)
    await col.delete_one({"_id": ObjectId(school_id)})
