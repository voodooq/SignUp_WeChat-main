import time
from typing import List
from app.repository import gym_repo, attempt_repo, user_repo
from app.utils.i18n import get_lang, t

def _format_gym(gym: dict, lang: str) -> dict:
    """根据语言格式化场馆信息"""
    res = {
        "id": str(gym["_id"]),
        "name": gym.get("name_en") if lang == "en" and gym.get("name_en") else gym.get("name"),
        "address": gym.get("address_en") if lang == "en" and gym.get("address_en") else gym.get("address"),
        "intro": gym.get("intro_en") if lang == "en" and gym.get("intro_en") else gym.get("intro"),
        "images": gym.get("images", []),
        "location": {"lng": gym.get("lng"), "lat": gym.get("lat")},
        "status": gym.get("status", "active"),
        "heat": gym.get("heat", 0),
        "distance": round(gym.get("distance", 0) / 1000, 1) if "distance" in gym else None  # 转换为公里
    }
    return res

async def list_gyms(lng: float = None, lat: float = None, sort_by: str = "heat") -> dict:
    lang = get_lang()
    query = {"status": "active"}
    
    if sort_by == "distance" and lng is not None and lat is not None:
        # 使用地理位置聚合查询并返回距离
        gyms = await gym_repo.find_gyms_with_distance(lng, lat, query)
    else:
        # 默认按热度排序
        gyms = await gym_repo.find_gyms(query)
        
    return {
        "code": 200,
        "data": [_format_gym(g, lang) for g in gyms]
    }

async def get_gym_detail(gym_id: str) -> dict:
    lang = get_lang()
    gym = await gym_repo.find_gym_by_id(gym_id)
    if not gym:
        return {"code": 404, "message": t("record_not_found")}
    
    routes = await gym_repo.find_routes_by_gym(gym_id)
    data = _format_gym(gym, lang)
    data["routes"] = [{
        "id": str(r["_id"]),
        "name": r.get("name"),
        "difficulty": r.get("difficulty"),
        "image_url": r.get("image_url"),
        "description": r.get("description")
    } for r in routes]
    
    return {"code": 200, "data": data}

# 管理员接口
async def admin_add_gym(data: dict) -> dict:
    data["create_time"] = int(time.time() * 1000)
    data["status"] = "active"
    gid = await gym_repo.create_gym(data)
    return {"code": 200, "message": t("success"), "data": {"id": gid}}

async def admin_update_gym(gym_id: str, data: dict) -> dict:
    await gym_repo.update_gym(gym_id, data)
    return {"code": 200, "message": t("success")}

async def admin_delete_gym(gym_id: str) -> dict:
    await gym_repo.update_gym(gym_id, {"status": "deleted"})
    return {"code": 200, "message": t("success")}

async def admin_add_route(data: dict) -> dict:
    data["create_time"] = int(time.time() * 1000)
    data["status"] = "active"
    rid = await gym_repo.create_route(data)
    return {"code": 200, "message": t("success"), "data": {"id": rid}}

async def submit_attempt(user_id: str, data: dict) -> dict:
    """提交完攀记录"""
    # 检查单人单线路限制（假设每人每线路限3次）
    existing = await attempt_repo.find_user_attempts_on_route(user_id, data["route_id"])
    if len(existing) >= 3:
        return {"code": 400, "message": t("error_limit_reached")}
    
    data["user_id"] = user_id
    aid = await attempt_repo.create_attempt(data)
    return {"code": 200, "message": t("success"), "data": {"id": aid}}

async def get_route_attempts(route_id: str) -> dict:
    """获取线路评价列表"""
    attempts = await attempt_repo.find_attempts_by_route(route_id)
    res_list = []
    for a in attempts:
        user = await user_repo.find_by_user_id(a["user_id"])
        res_list.append({
            "id": str(a["_id"]),
            "user_nickname": user.get("nickname", "攀登者") if user else "攀登者",
            "user_avatar": user.get("avatar", "") if user else "",
            "video_url": a.get("video_url"),
            "rating": a.get("rating"),
            "comment": a.get("comment"),
            "create_time": a.get("create_time")
        })
    return {"code": 200, "data": res_list}
