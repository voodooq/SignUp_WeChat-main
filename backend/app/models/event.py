from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RankingItem(BaseModel):
    """排名项"""
    rank: int
    name: str
    video_url: Optional[str] = ""

class EventBase(BaseModel):
    """赛事基础模型"""
    title: str = Field(..., description="赛事标题")
    category: str = Field(..., description="赛事分类 (赛事一/二/三/四)")
    banner_url: str = Field("", description="封面图链接")
    
    # 时间相关
    event_start_time: int = Field(..., description="比赛开始时间戳 (ms)")
    event_end_time: int = Field(..., description="比赛结束时间戳 (ms)")
    reg_start_time: int = Field(..., description="报名开始时间戳 (ms)")
    reg_end_time: int = Field(..., description="报名结束时间戳 (ms)")
    
    # 内容相关
    intro: str = Field("", description="赛事介绍")
    news: List[str] = Field([], description="相关新闻列表")
    reviews: List[str] = Field([], description="精彩回顾列表")
    highlight_videos: List[str] = Field([], description="精彩视频 URL 列表")
    
    # 实况相关
    live_url: Optional[str] = Field("", description="多赛场直播链接")
    process_status: str = Field("not_started", description="赛事进程 (not_started/ongoing/finished)")
    
    # 地点相关
    address: str = Field("", description="赛事地址")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # 排名相关
    rankings: List[RankingItem] = Field([], description="实时名次展示")
    
    sort_order: int = 0

class EventCreate(EventBase):
    """创建赛事请求"""
    pass

class EventUpdate(BaseModel):
    """更新赛事请求"""
    title: Optional[str] = None
    category: Optional[str] = None
    banner_url: Optional[str] = None
    event_start_time: Optional[int] = None
    event_end_time: Optional[int] = None
    reg_start_time: Optional[int] = None
    reg_end_time: Optional[int] = None
    intro: Optional[str] = None
    news: Optional[List[str]] = None
    reviews: Optional[List[str]] = None
    highlight_videos: Optional[List[str]] = None
    live_url: Optional[str] = None
    process_status: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rankings: Optional[List[RankingItem]] = None
    sort_order: Optional[int] = None

class EventInDB(EventBase):
    """数据库中的赛事"""
    id: str = Field(..., alias="_id")
    create_time: int
    update_time: Optional[int] = None
