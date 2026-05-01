"""
轮播图 / 赛事图片 / 参赛须知图片数据访问层
"""
import time
from typing import Optional, List
from bson import ObjectId
from app.database import get_collection


# ========== 通用图片 CRUD ==========

async def _list_images(collection: str, where: dict = None, sort_field: str = "sort_order") -> List[dict]:
    """通用图片列表查询"""
    col = get_collection(collection)
    cursor = col.find(where or {}).sort(sort_field, 1)
    return await cursor.to_list(length=500)


async def _create_image(collection: str, doc: dict) -> str:
    """通用图片创建"""
    col = get_collection(collection)
    doc["create_time"] = int(time.time() * 1000)
    result = await col.insert_one(doc)
    return str(result.inserted_id)


async def _update_image(collection: str, image_id: str, update_data: dict) -> None:
    """通用图片更新"""
    col = get_collection(collection)
    update_data["update_time"] = int(time.time() * 1000)
    await col.update_one({"_id": ObjectId(image_id)}, {"$set": update_data})


async def _find_image(collection: str, image_id: str) -> Optional[dict]:
    """根据 ID 查找图片"""
    col = get_collection(collection)
    return await col.find_one({"_id": ObjectId(image_id)})


async def _delete_image(collection: str, image_id: str) -> None:
    """删除图片"""
    col = get_collection(collection)
    await col.delete_one({"_id": ObjectId(image_id)})


# ========== 轮播图 ==========

BANNER_COLLECTION = "sign_banners"


async def list_banners(position: str = None) -> List[dict]:
    where = {}
    if position:
        where["position"] = position
    return await _list_images(BANNER_COLLECTION, where)


async def list_active_banners(position: str) -> List[dict]:
    return await _list_images(BANNER_COLLECTION, {"position": position, "status": "active"})


async def create_banner(doc: dict) -> str:
    return await _create_image(BANNER_COLLECTION, doc)


async def update_banner(banner_id: str, data: dict) -> None:
    await _update_image(BANNER_COLLECTION, banner_id, data)


async def find_banner(banner_id: str) -> Optional[dict]:
    return await _find_image(BANNER_COLLECTION, banner_id)


async def delete_banner(banner_id: str) -> None:
    await _delete_image(BANNER_COLLECTION, banner_id)


# ========== 赛事信息图片 ==========

EVENT_IMAGE_COLLECTION = "sign_event_images"


async def list_event_images() -> List[dict]:
    return await _list_images(EVENT_IMAGE_COLLECTION)


async def list_active_event_images() -> List[dict]:
    return await _list_images(EVENT_IMAGE_COLLECTION, {"status": "active"})


async def create_event_image(doc: dict) -> str:
    return await _create_image(EVENT_IMAGE_COLLECTION, doc)


async def update_event_image(image_id: str, data: dict) -> None:
    await _update_image(EVENT_IMAGE_COLLECTION, image_id, data)


async def find_event_image(image_id: str) -> Optional[dict]:
    return await _find_image(EVENT_IMAGE_COLLECTION, image_id)


async def delete_event_image(image_id: str) -> None:
    await _delete_image(EVENT_IMAGE_COLLECTION, image_id)


# ========== 参赛须知图片 ==========

NOTICE_IMAGE_COLLECTION = "sign_notice_images"


async def list_notice_images() -> List[dict]:
    return await _list_images(NOTICE_IMAGE_COLLECTION)


async def list_active_notice_images() -> List[dict]:
    return await _list_images(NOTICE_IMAGE_COLLECTION, {"status": "active"})


async def create_notice_image(doc: dict) -> str:
    return await _create_image(NOTICE_IMAGE_COLLECTION, doc)


async def update_notice_image(image_id: str, data: dict) -> None:
    await _update_image(NOTICE_IMAGE_COLLECTION, image_id, data)


async def find_notice_image(image_id: str) -> Optional[dict]:
    return await _find_image(NOTICE_IMAGE_COLLECTION, image_id)


async def delete_notice_image(image_id: str) -> None:
    await _delete_image(NOTICE_IMAGE_COLLECTION, image_id)


async def reorder_notice_images(ordered_ids: List[str]) -> None:
    """重新排序参赛须知图片"""
    col = get_collection(NOTICE_IMAGE_COLLECTION)
    for i, image_id in enumerate(ordered_ids):
        await col.update_one(
            {"_id": ObjectId(image_id)},
            {"$set": {"sort_order": i, "update_time": int(time.time() * 1000)}},
        )
