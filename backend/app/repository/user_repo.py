"""
用户数据访问层
"""
from typing import Optional
from bson import ObjectId
from app.database import get_collection

COLLECTION = "sign_users"


async def find_by_openid(openid: str) -> Optional[dict]:
    """根据 openid 查找用户"""
    col = get_collection(COLLECTION)
    return await col.find_one({"openid": openid})


async def create_user(openid: str, role: str = "user") -> str:
    """创建用户，返回用户 ID"""
    col = get_collection(COLLECTION)
    import time
    doc = {
        "openid": openid,
        "role": role,
        "create_time": int(time.time() * 1000),
    }
    result = await col.insert_one(doc)
    return str(result.inserted_id)


async def update_login_time(user_id: str) -> None:
    """更新最后登录时间"""
    col = get_collection(COLLECTION)
    import time
    await col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"update_time": int(time.time() * 1000)}},
    )


async def ensure_admin_exists() -> None:
    """确保数据库中存在 admin 用户"""
    col = get_collection(COLLECTION)
    admin = await col.find_one({"openid": "admin"})
    if not admin:
        import time
        await col.insert_one({
            "openid": "admin",
            "role": "admin",
            "create_time": int(time.time() * 1000),
        })
