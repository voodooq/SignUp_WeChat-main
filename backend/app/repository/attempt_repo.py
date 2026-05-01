import time
from typing import List, Optional
from bson import ObjectId
from app.database import get_collection

COLLECTION_ATTEMPTS = "sign_route_attempts"

async def create_attempt(doc: dict) -> str:
    col = get_collection(COLLECTION_ATTEMPTS)
    doc["create_time"] = int(time.time() * 1000)
    doc["status"] = "approved"  # 默认通过，后续可加人工审核
    result = await col.insert_one(doc)
    return str(result.inserted_id)

async def find_attempts_by_route(route_id: str) -> List[dict]:
    col = get_collection(COLLECTION_ATTEMPTS)
    cursor = col.find({"route_id": route_id, "status": "approved"}).sort("create_time", -1)
    return await cursor.to_list(length=100)

async def find_user_attempts_on_route(user_id: str, route_id: str) -> List[dict]:
    col = get_collection(COLLECTION_ATTEMPTS)
    cursor = col.find({"user_id": user_id, "route_id": route_id})
    return await cursor.to_list(length=10)
