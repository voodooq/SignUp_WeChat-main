"""
报名相关 API 路由
"""
from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user, get_optional_user
from app.service import register_service, admin_service
from app.models.registration import (
    RegistrationSubmit,
    UpdateAvatarRequest,
    CheckDuplicateRequest,
)

router = APIRouter(prefix="/api/register", tags=["报名"])


@router.post("/submit")
async def submit(
    req: RegistrationSubmit,
    current_user: dict = Depends(get_current_user),
):
    """提交报名"""
    return await register_service.submit_registration(
        current_user["openid"], req.model_dump()
    )


@router.post("/update-avatar")
async def update_avatar(
    req: UpdateAvatarRequest,
    current_user: dict = Depends(get_current_user),
):
    """更新报名头像"""
    return await register_service.update_avatar(
        current_user["openid"], req.ticket_no, req.avatar_url
    )


@router.post("/check-duplicate")
async def check_duplicate(req: CheckDuplicateRequest):
    """检查重复报名（无需登录）"""
    return await register_service.check_duplicate(req.id_card)


@router.get("/ticket/{ticket_no}")
async def get_ticket_info(ticket_no: str):
    """查看证书"""
    return await register_service.get_ticket_info(ticket_no)

@router.get("/leaderboard/{comp_id}")
async def get_leaderboard(comp_id: str):
    """获取赛事排行榜"""
    return await admin_service.get_competition_leaderboard(comp_id)


@router.get("/settings")
async def get_settings():
    # Public settings for miniapp
    return await register_service.get_settings()


@router.get("/test")
async def test():
    return {"message": "register router is working"}


@router.get("/notice-images")
async def list_notice_images():
    """获取参赛须知图片（无需登录）"""
    return await register_service.list_notice_images()


@router.get("/my-registrations")
async def get_my_registrations(
    current_user: dict = Depends(get_current_user),
):
    """获取当前用户所有报名记录"""
    return await register_service.get_my_registrations(current_user["openid"])


@router.get("/ticket")
async def get_ticket(
    ticket_no: str = Query(..., description="证书编号"),
    current_user: dict = Depends(get_optional_user),
):
    """获取证书信息"""
    openid = current_user["openid"] if current_user else None
    return await register_service.get_ticket(ticket_no, openid)


@router.get("/my-scores")
async def get_my_scores(
    current_user: dict = Depends(get_current_user),
):
    """查询当前用户的成绩"""
    return await register_service.get_my_scores(current_user["openid"])


@router.get("/scores-by-ticket")
async def get_scores_by_ticket(
    ticket_no: str = Query(..., description="证书编号"),
):
    """按证书编号查询成绩（无需登录）"""
    return await register_service.get_scores_by_ticket_no(ticket_no)


@router.get("/banners")
async def get_banners(position: str = Query("top")):
    """获取轮播图（无需登录，首页使用）"""
    from app.repository import image_repo
    items = await image_repo.list_active_banners(position)
    return {"code": 200, "data": [{**b, "_id": str(b["_id"])} for b in items]}


@router.get("/event-images")
async def get_event_images():
    """获取赛事信息图片（无需登录，首页使用）"""
    from app.repository import image_repo
    items = await image_repo.list_active_event_images()
    return {"code": 200, "data": [{**i, "_id": str(i["_id"])} for i in items]}


@router.get("/events")
async def get_events():
    """获取赛事项目列表（无需登录，报名页使用）"""
    from app.repository import event_repo
    items = await event_repo.list_events()
    active = [e for e in items if e.get("status") == "active"]
    return {"code": 200, "data": [{**e, "_id": str(e["_id"])} for e in active]}


@router.get("/schools")
async def get_schools():
    """获取学校列表（无需登录，报名页使用）"""
    from app.repository import setting_repo
    items = await setting_repo.list_schools()
    active = [s for s in items if s.get("status") == "active"]
    return {"code": 200, "data": [{**s, "_id": str(s["_id"])} for s in active]}


@router.get("/competitions")
async def get_competitions():
    """获取赛事列表（无需登录，首页 Level 2 使用）"""
    return await admin_service.list_competitions()


@router.get("/competition/{comp_id}")
async def get_competition_detail(comp_id: str):
    """获取赛事详情（无需登录）"""
    from app.database import get_collection
    from bson import ObjectId
    col = get_collection("sign_competitions")
    try:
        item = await col.find_one({"_id": ObjectId(comp_id), "status": {"$ne": "deleted"}})
        if not item:
            return {"code": 404, "message": "赛事不存在"}
        item["_id"] = str(item["_id"])
        return {"code": 200, "data": item}
    except Exception:
        return {"code": 400, "message": "无效的赛事ID"}
