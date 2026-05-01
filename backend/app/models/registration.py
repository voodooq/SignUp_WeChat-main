"""
报名记录相关数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class RegistrationSubmit(BaseModel):
    """报名提交请求"""
    name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern=r"^(male|female)$")
    clothes_size: str = Field("", max_length=10)
    school: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=11, max_length=11)
    id_card: str = Field(..., min_length=18, max_length=18)
    avatar_url: str = Field("", max_length=500)
    required_event: str = Field(..., min_length=1, max_length=50)
    optional_events: List[str] = Field(..., min_length=2)
    event_name: str = Field("", max_length=200)
    is_sports_talent: bool = False
    personal_promise_signature: str = Field(..., min_length=1)
    health_promise_signature: str = Field(..., min_length=1)
    personal_guardian_signature: str = Field(..., min_length=1)
    health_guardian_signature: str = Field(..., min_length=1)


class UpdateAvatarRequest(BaseModel):
    """更新头像请求"""
    ticket_no: str = Field(..., min_length=1)
    avatar_url: str = Field(..., min_length=1, max_length=500)


class CheckDuplicateRequest(BaseModel):
    """检查重复报名请求"""
    id_card: str = Field(..., min_length=18, max_length=18)


class RegistrationItem(BaseModel):
    """报名记录列表项"""
    _id: str = ""
    ticket_no: str = ""
    name: str = ""
    gender: str = ""
    clothes_size: str = ""
    school: str = ""
    phone: str = ""
    avatar_url: str = ""
    id_card_masked: str = ""
    required_event: str = ""
    optional_events: List[str] = []
    event_name: str = ""
    payment_status: str = "unpaid"
    registered_by: str = "self"
    create_time: Optional[int] = None
    fee: int = 0


class TicketInfo(BaseModel):
    """准考证信息"""
    _id: str = ""
    ticket_no: str = ""
    name: str = ""
    gender: str = ""
    clothes_size: str = ""
    school: str = ""
    phone: str = ""
    avatar_url: str = ""
    id_card_masked: str = ""
    required_event: str = ""
    optional_events: List[str] = []
    event_name: str = ""
    is_sports_talent: bool = False
    payment_status: str = ""
    payment_order_no: str = ""
    create_time: Optional[int] = None
