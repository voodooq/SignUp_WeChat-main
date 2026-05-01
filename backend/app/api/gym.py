from fastapi import APIRouter, Depends, Query
from app.service import gym_service
from app.models.admin import GymCreate, GymUpdate, RouteCreate, AttemptCreate
from app.dependencies import get_current_admin, get_current_user

router = APIRouter(prefix="/api/gym", tags=["场馆服务"])

@router.get("/list")
async def list_gyms(
    lng: float = Query(None), 
    lat: float = Query(None), 
    sort_by: str = Query("heat", pattern="^(heat|distance)$")
):
    """获取场馆列表（小程序端，支持热度或距离排序）"""
    return await gym_service.list_gyms(lng, lat, sort_by)

@router.get("/{gym_id}")
async def get_gym_detail(gym_id: str):
    """获取场馆详情及线路（小程序端）"""
    return await gym_service.get_gym_detail(gym_id)

@router.post("/attempt")
async def submit_attempt(req: AttemptCreate, user: dict = Depends(get_current_user)):
    """提交完攀记录及视频（小程序端）"""
    return await gym_service.submit_attempt(user["user_id"], req.model_dump())

@router.get("/route/{route_id}/attempts")
async def get_route_attempts(route_id: str):
    """获取线路完攀评价列表（小程序端）"""
    return await gym_service.get_route_attempts(route_id)

# 管理后台接口
@router.post("/admin/add")
async def add_gym(req: GymCreate, _admin: dict = Depends(get_current_admin)):
    """新增场馆（管理端）"""
    return await gym_service.admin_add_gym(req.model_dump())

@router.put("/admin/{gym_id}")
async def update_gym(gym_id: str, req: GymUpdate, _admin: dict = Depends(get_current_admin)):
    """修改场馆（管理端）"""
    return await gym_service.admin_update_gym(gym_id, req.model_dump(exclude_none=True))

@router.delete("/admin/{gym_id}")
async def delete_gym(gym_id: str, _admin: dict = Depends(get_current_admin)):
    """删除场馆（管理端）"""
    return await gym_service.admin_delete_gym(gym_id)

@router.post("/admin/route/add")
async def add_route(req: RouteCreate, _admin: dict = Depends(get_current_admin)):
    """新增线路（管理端）"""
    return await gym_service.admin_add_route(req.model_dump())
