"""
支付相关 API 路由（第二阶段完善）
"""
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.service import payment_service
from app.models.admin import CreateOrderRequest, MockPayRequest, QueryOrderRequest

router = APIRouter(prefix="/api/payment", tags=["支付"])


@router.post("/create-order")
async def create_order(
    req: CreateOrderRequest,
    current_user: dict = Depends(get_current_user),
):
    """创建支付订单"""
    return await payment_service.create_order(
        current_user["openid"], req.registration_id
    )


@router.post("/mock-pay")
async def mock_pay(
    req: MockPayRequest,
    current_user: dict = Depends(get_current_user),
):
    """模拟支付（仅开发环境）"""
    return await payment_service.mock_pay(
        current_user["openid"], req.registration_id
    )


@router.post("/query-order")
async def query_order(
    req: QueryOrderRequest,
    current_user: dict = Depends(get_current_user),
):
    """查询订单状态"""
    return await payment_service.query_order(
        current_user["openid"], req.registration_id
    )


@router.get("/subscribe-config")
async def subscribe_config():
    """获取订阅消息配置"""
    from app.config import settings
    return {
        "code": 200,
        "data": {"template_id": settings.WECHAT_SUBSCRIBE_TEMPLATE_ID},
    }
