from typing import List, Optional
from bson import ObjectId
from app.database import get_collection

COLLECTION_GYMS = "sign_gyms"
COLLECTION_ROUTES = "sign_routes"

async def init_gym_indices():
    """初始化 2dsphere 索引以支持距离排序"""
    col = get_collection(COLLECTION_GYMS)
    import pymongo
    await col.create_index([("location", pymongo.GEOSPHERE)])

async def create_gym(doc: dict) -> str:
    col = get_collection(COLLECTION_GYMS)
    # 转换为 GeoJSON Point 格式以支持索引
    if "lng" in doc and "lat" in doc:
        doc["location"] = {
            "type": "Point",
            "coordinates": [doc["lng"], doc["lat"]]
        }
    result = await col.insert_one(doc)
    return str(result.inserted_id)

async def find_gyms(query: dict = {}, sort: list = [("heat", -1), ("create_time", -1)]) -> List[dict]:
    col = get_collection(COLLECTION_GYMS)
    cursor = col.find(query).sort(sort)
    return await cursor.to_list(length=100)

async def find_gym_by_id(gym_id: str) -> Optional[dict]:
    col = get_collection(COLLECTION_GYMS)
    return await col.find_one({"_id": ObjectId(gym_id)})

async def update_gym(gym_id: str, update: dict):
    col = get_collection(COLLECTION_GYMS)
    await col.update_one({"_id": ObjectId(gym_id)}, {"$set": update})

# 线路相关
async def find_gyms_near(lng: float, lat: float, query: dict = {}) -> List[dict]:
    """仅排序，不返回距离"""
    col = get_collection(COLLECTION_GYMS)
    query["location"] = {
        "$near": {
            "$geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            }
        }
    }
    cursor = col.find(query)
    return await cursor.to_list(length=100)

async def find_gyms_with_distance(lng: float, lat: float, query: dict = {}) -> List[dict]:
    """使用聚合框架返回距离字段 distance (米)"""
    col = get_collection(COLLECTION_GYMS)
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lng, lat]},
                "distanceField": "distance",
                "query": query,
                "spherical": True
            }
        }
    ]
    cursor = col.aggregate(pipeline)
    return await cursor.to_list(length=100)

# 线路相关
async def create_route(doc: dict) -> str:
    col = get_collection(COLLECTION_ROUTES)
    result = await col.insert_one(doc)
    return str(result.inserted_id)

async def find_routes_by_gym(gym_id: str) -> List[dict]:
    col = get_collection(COLLECTION_ROUTES)
    cursor = col.find({"gym_id": gym_id, "status": {"$ne": "deleted"}})
    return await cursor.to_list(length=200)

async def find_route_by_id(route_id: str) -> Optional[dict]:
    col = get_collection(COLLECTION_ROUTES)
    return await col.find_one({"_id": ObjectId(route_id)})
