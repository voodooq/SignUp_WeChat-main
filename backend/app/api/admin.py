"""
管理员相关 API 路由
"""
from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_admin
from app.service import admin_service
from app.models.admin import (
    EventCreate, EventUpdate,
    BannerCreate, BannerUpdate,
    ImageCreate, ImageUpdate, ReorderRequest,
    SettingsUpdate,
    SchoolCreate, SchoolUpdate,
    ScoreImport,
    ManualRegisterRequest,
    CompetitionCreate, CompetitionUpdate,
)
from fastapi.security import OAuth2PasswordRequestForm
from app.config import settings
from app.utils.security import create_access_token


router = APIRouter(prefix="/api/admin", tags=["管理后台"])


# ========== 登录授权 ==========

@router.post("/login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """管理员登录"""
    if form_data.username != settings.ADMIN_USERNAME or form_data.password != settings.ADMIN_PASSWORD:
        return {"code": 401, "message": "账号或密码错误"}
    
    # 签发 Token，openid 设为 admin 以区分普通微信用户
    token = create_access_token({"openid": "admin", "role": "admin"})
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": token,
            "token_type": "bearer"
        }
    }


# ========== 报名查询 ==========

@router.get("/registrations")
async def search_registrations(
    keyword: str = Query("", description="搜索关键词"),
    event_item: str = Query("", description="按项目筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _admin: dict = Depends(get_current_admin),
):
    """搜索报名记录"""
    return await admin_service.search_registration(keyword, event_item, page, page_size)


@router.get("/registration/{registration_id}")
async def get_registration_detail(
    registration_id: str,
    _admin: dict = Depends(get_current_admin),
):
    """获取报名详情"""
    return await admin_service.get_registration_detail(registration_id)


@router.get("/metrics")
async def get_registration_stats(
    _admin: dict = Depends(get_current_admin),
):
    """获取报名统计"""
    return await admin_service.get_registration_stats()


# ========== 手动报名 ==========

@router.post("/manual-register")
async def manual_register(
    req: ManualRegisterRequest,
    admin: dict = Depends(get_current_admin),
):
    """管理员手动报名"""
    return await admin_service.manual_register(admin["user_id"], req.model_dump())


# ========== 项目管理 ==========

@router.get("/events")
async def list_events(_admin: dict = Depends(get_current_admin)):
    return await admin_service.list_events()


@router.post("/events")
async def add_event(req: EventCreate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.add_event(req.model_dump())


@router.put("/events/{event_id}")
async def update_event(event_id: str, req: EventUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_event(event_id, req.model_dump(exclude_none=True))


@router.delete("/events/{event_id}")
async def delete_event(event_id: str, _admin: dict = Depends(get_current_admin)):
    return await admin_service.delete_event(event_id)


# ========== 轮播图管理 ==========

@router.get("/banners")
async def list_banners(position: str = Query(None), _admin: dict = Depends(get_current_admin)):
    return await admin_service.list_banners(position)


@router.post("/banners")
async def add_banner(req: BannerCreate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.add_banner(req.model_dump())


@router.put("/banners/{banner_id}")
async def update_banner(banner_id: str, req: BannerUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_banner(banner_id, req.model_dump(exclude_none=True))


@router.delete("/banners/{banner_id}")
async def delete_banner(banner_id: str, _admin: dict = Depends(get_current_admin)):
    return await admin_service.delete_banner(banner_id)


# ========== 赛事图片管理 ==========

@router.get("/event-images")
async def list_event_images(_admin: dict = Depends(get_current_admin)):
    return await admin_service.list_event_images()


@router.post("/event-images")
async def add_event_image(req: ImageCreate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.add_event_image(req.model_dump())


@router.put("/event-images/{image_id}")
async def update_event_image(image_id: str, req: ImageUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_event_image(image_id, req.model_dump(exclude_none=True))


@router.delete("/event-images/{image_id}")
async def delete_event_image(image_id: str, _admin: dict = Depends(get_current_admin)):
    return await admin_service.delete_event_image(image_id)


# ========== 须知图片管理 ==========

@router.get("/notice-images")
async def list_notice_images(_admin: dict = Depends(get_current_admin)):
    return await admin_service.list_notice_images()


@router.post("/notice-images")
async def add_notice_image(req: ImageCreate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.add_notice_image(req.model_dump())


@router.put("/notice-images/{image_id}")
async def update_notice_image(image_id: str, req: ImageUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_notice_image(image_id, req.model_dump(exclude_none=True))


@router.delete("/notice-images/{image_id}")
async def delete_notice_image(image_id: str, _admin: dict = Depends(get_current_admin)):
    return await admin_service.delete_notice_image(image_id)


@router.post("/notice-images/reorder")
async def reorder_notice_images(req: ReorderRequest, _admin: dict = Depends(get_current_admin)):
    return await admin_service.reorder_notice_images(req.ordered_ids)


# ========== 赛事设置 ==========

@router.get("/settings")
async def get_settings(_admin: dict = Depends(get_current_admin)):
    return await admin_service.get_settings()


@router.put("/settings")
async def update_settings(req: SettingsUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_settings(req.settings)


# ========== 学校管理 ==========

@router.get("/schools")
async def list_schools(_admin: dict = Depends(get_current_admin)):
    return await admin_service.list_schools()


@router.post("/schools")
async def add_school(req: SchoolCreate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.add_school(req.name, req.sort_order)


@router.put("/schools/{school_id}")
async def update_school(school_id: str, req: SchoolUpdate, _admin: dict = Depends(get_current_admin)):
    return await admin_service.update_school(school_id, req.model_dump(exclude_none=True))


@router.delete("/schools/{school_id}")
async def delete_school(school_id: str, _admin: dict = Depends(get_current_admin)):
    return await admin_service.delete_school(school_id)


# ========== 赛事 (Competition) 管理 ==========

@router.get("/competitions")
async def list_competitions(_admin: dict = Depends(get_current_admin)):
    """列表获取所有赛事"""
    return await admin_service.list_competitions()


@router.post("/competitions")
async def add_competition(req: CompetitionCreate, _admin: dict = Depends(get_current_admin)):
    """创建新赛事"""
    return await admin_service.add_competition(req.model_dump())


@router.put("/competitions/{comp_id}")
async def update_competition(comp_id: str, req: CompetitionUpdate, _admin: dict = Depends(get_current_admin)):
    """修改赛事信息"""
    return await admin_service.update_competition(comp_id, req.model_dump(exclude_none=True))


@router.delete("/competitions/{comp_id}")
async def delete_competition(comp_id: str, _admin: dict = Depends(get_current_admin)):
    """删除赛事"""
    return await admin_service.delete_competition(comp_id)


# ========== 成绩管理 ==========

@router.post("/scores/import")
async def import_scores(req: ScoreImport, _admin: dict = Depends(get_current_admin)):
    return await admin_service.import_scores([s.model_dump() for s in req.scores])


@router.delete("/scores")
async def clear_scores(_admin: dict = Depends(get_current_admin)):
    return await admin_service.clear_scores()


@router.get("/scores")
async def list_scores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
    _admin: dict = Depends(get_current_admin),
):
    return await admin_service.list_scores(page, page_size, keyword)


@router.get("/export-students")
async def export_students(_admin: dict = Depends(get_current_admin)):
    return await admin_service.export_students()
