"""
赛事项目 / 成绩 / 轮播图 / 图片 / 设置 / 学校相关数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ========== 赛事项目 ==========

class EventCreate(BaseModel):
    """创建赛事项目"""
    name: str = Field(..., min_length=1, max_length=50)
    fee: int = Field(0, ge=0, description="费用，单位：分")
    code: str = Field("00", max_length=10)
    sort_order: int = 0
    is_required: bool = False


class EventUpdate(BaseModel):
    """更新赛事项目"""
    name: Optional[str] = None
    fee: Optional[int] = None
    code: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


# ========== 轮播图 ==========

class BannerCreate(BaseModel):
    """创建轮播图"""
    image_url: str = Field(..., min_length=1)
    position: str = Field(..., pattern=r"^(top|bottom)$")
    sort_order: int = 0


class BannerUpdate(BaseModel):
    """更新轮播图"""
    image_url: Optional[str] = None
    position: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


# ========== 图片（赛事信息 / 参赛须知） ==========

class ImageCreate(BaseModel):
    """创建图片"""
    image_url: str = Field(..., min_length=1)
    sort_order: int = 0


class ImageUpdate(BaseModel):
    """更新图片"""
    sort_order: Optional[int] = None
    status: Optional[str] = None


class ReorderRequest(BaseModel):
    """排序请求"""
    ordered_ids: List[str] = Field(..., min_length=1)


# ========== 赛事 (Competition) ==========

class CompetitionCreate(BaseModel):
    """创建赛事"""
    title: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    poster_url: Optional[str] = ""
    start_time: str = Field(..., description="比赛时间 YYYY-MM-DD HH:mm:ss")
    reg_start_time: str = Field(..., description="报名开始时间 YYYY-MM-DD HH:mm:ss")
    reg_end_time: str = Field(..., description="报名截止时间 YYYY-MM-DD HH:mm:ss")
    comp_type: str = Field("general", pattern=r"^(general|bouldering|speed)$")
    contact_name: Optional[str] = ""
    contact_phone: Optional[str] = ""
    # 新增三级功能字段
    intro: Optional[str] = ""
    news: List[str] = []
    reviews: List[str] = []
    live_url: Optional[str] = ""
    rankings: List[Dict[str, Any]] = []
    # 新增分类与结构化类目
    type: str = Field("event", pattern=r"^(event|activity)$")
    categories: List[Dict[str, Any]] = []  # 结构化类目，支持多级选择与余量控制
    lng: Optional[float] = None
    lat: Optional[float] = None
    detail_images: List[str] = []
    description: Optional[str] = "" # 简短描述，显示在列表页


class CompetitionUpdate(BaseModel):
    """更新赛事"""
    title: Optional[str] = None
    location: Optional[str] = None
    poster_url: Optional[str] = None
    start_time: Optional[str] = None
    reg_start_time: Optional[str] = None
    reg_end_time: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None
    # 新增三级功能字段
    intro: Optional[str] = None
    news: Optional[List[str]] = None
    reviews: Optional[List[str]] = None
    live_url: Optional[str] = None
    rankings: Optional[List[Dict[str, Any]]] = None
    type: Optional[str] = None
    categories: Optional[List[Dict[str, Any]]] = None
    lng: Optional[float] = None
    lat: Optional[float] = None
    detail_images: Optional[List[str]] = None
    description: Optional[str] = None


# ========== 赛事设置 ==========

class SettingsUpdate(BaseModel):
    """更新设置"""
    settings: Dict[str, str]


# ========== 学校 ==========

class SchoolCreate(BaseModel):
    """创建学校"""
    name: str = Field(..., min_length=1, max_length=100)
    sort_order: int = 0


class SchoolUpdate(BaseModel):
    """更新学校"""
    name: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


# ========== 成绩 ==========

class ScoreItem(BaseModel):
    """成绩导入项"""
    ticket_no: str
    name: str
    event_name: str
    score: Optional[str] = ""
    time_ms: Optional[int] = 0  # 毫秒级计时
    points: Optional[str] = ""
    remark: Optional[str] = ""


class ScoreImport(BaseModel):
    """成绩批量导入"""
    scores: List[ScoreItem] = Field(..., min_length=1, max_length=5000)


# ========== 手动报名 ==========

class ManualRegisterRequest(BaseModel):
    """管理员手动报名"""
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern=r"^(male|female)$")
    clothes_size: str = Field("", max_length=10)
    school: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=11, max_length=11)
    id_card: str = Field(..., min_length=18, max_length=18)
    required_event: str = Field(..., min_length=1, max_length=50)
    optional_events: List[str] = Field(..., min_length=2)
    event_name: str = Field("", max_length=200)
    is_sports_talent: bool = False


# ========== 支付（第二阶段） ==========

class CreateOrderRequest(BaseModel):
    """创建支付订单"""
    registration_id: str


class QueryOrderRequest(BaseModel):
    """查询订单"""
    registration_id: str


class MockPayRequest(BaseModel):
    """模拟支付"""
    registration_id: str
# ========== 攀岩馆 ==========

class GymCreate(BaseModel):
    """创建场馆"""
    name: str = Field(..., min_length=1)
    name_en: Optional[str] = ""
    address: str = Field(..., min_length=1)
    address_en: Optional[str] = ""
    lng: float
    lat: float
    intro: Optional[str] = ""
    intro_en: Optional[str] = ""
    images: List[str] = []
    heat: int = Field(0, ge=0, description="热度/推荐权重")

class GymUpdate(BaseModel):
    """更新场馆"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    address: Optional[str] = None
    address_en: Optional[str] = None
    lng: Optional[float] = None
    lat: Optional[float] = None
    intro: Optional[str] = None
    intro_en: Optional[str] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None
    heat: Optional[int] = None

# ========== 线路 ==========

class RouteCreate(BaseModel):
    """创建线路"""
    gym_id: str
    name: str = Field(..., min_length=1)
    difficulty: str = Field(..., min_length=1)
    description: Optional[str] = ""
    image_url: str
    qr_code: Optional[str] = ""

class RouteUpdate(BaseModel):
    """更新线路"""
    name: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
# ========== 完攀记录 ==========

class AttemptCreate(BaseModel):
    """提交完攀记录"""
    route_id: str
    video_url: str
    rating: int = Field(5, ge=1, le=5)
    comment: Optional[str] = ""

class AttemptUpdate(BaseModel):
    """审核/更新完攀记录"""
    status: str # approved / rejected
