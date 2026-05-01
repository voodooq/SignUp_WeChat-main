from pydantic import BaseModel, Field
from typing import List, Optional

class RouteItem(BaseModel):
    """岩馆线路"""
    id: str = Field(..., description="线路唯一标识")
    name: str = Field(..., description="线路名称")
    difficulty: str = Field(..., description="难度等级 (如 V1, V2)")
    style: str = Field("", description="线路风格")
    image_url: str = Field("", description="线路图片")
    video_url: str = Field("", description="完攀参考视频")

class Evaluation(BaseModel):
    """用户评价"""
    user_nickname: str
    user_avatar: str
    score: int = Field(5, ge=1, le=5)
    content: str
    video_url: Optional[str] = ""
    create_time: int

class GymBase(BaseModel):
    """岩馆基础模型"""
    name: str = Field(..., description="岩馆名称")
    logo_url: str = Field("", description="岩馆 Logo")
    banner_url: str = Field("", description="展示头图")
    
    # 核心信息
    intro: str = Field("", description="岩馆介绍")
    address: str = Field("", description="详细地址")
    contact_phone: str = Field("", description="联系电话")
    contact_wechat: str = Field("", description="联系微信")
    
    # LBS
    latitude: float
    longitude: float
    
    # 线路与交互
    routes: List[RouteItem] = Field([], description="线路展示")
    evaluations: List[Evaluation] = Field([], description="岩馆评价")
    
    sort_order: int = 0

class GymCreate(GymBase):
    """创建岩馆请求"""
    pass

class GymUpdate(BaseModel):
    """更新岩馆请求"""
    name: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    intro: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_wechat: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    routes: Optional[List[RouteItem]] = None
    sort_order: Optional[int] = None

class GymInDB(GymBase):
    """数据库中的岩馆"""
    id: str = Field(..., alias="_id")
    create_time: int
    update_time: Optional[int] = None
