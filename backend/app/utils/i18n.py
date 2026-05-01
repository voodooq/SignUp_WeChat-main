from contextvars import ContextVar
from fastapi import Request
from typing import Optional

# 使用 ContextVar 存储当前请求的语言，确保异步安全
_lang: ContextVar[str] = ContextVar("lang", default="zh")

def get_lang() -> str:
    """获取当前请求的语言"""
    return _lang.get()

def set_lang(lang: Optional[str]):
    """设置当前请求的语言"""
    if not lang:
        _lang.set("zh")
        return
    # 仅支持中英
    if lang.lower() in ["en", "english"] or lang.lower().startswith("en"):
        _lang.set("en")
    else:
        _lang.set("zh")

# 简易词典示例（后续可根据需要扩展到 JSON 文件）
TRANSLATIONS = {
    "zh": {
        "success": "操作成功",
        "error_unauthorized": "未授权访问",
        "error_not_found": "资源未找到",
        "login_success": "登录成功",
        "user_not_found": "用户不存在",
        "register_deadline_reached": "报名已截止",
        "register_success": "报名成功",
        "record_not_found": "记录未找到",
        "error_no_permission": "无权限操作",
        "error_input_invalid": "输入数据无效",
        "error_duplicate": "请勿重复提交",
        "error_id_card": "身份证号错误",
        "error_phone": "手机号错误",
        "error_limit_reached": "次数已达上限",
    },
    "en": {
        "success": "Operation successful",
        "error_unauthorized": "Unauthorized access",
        "error_not_found": "Resource not found",
        "login_success": "Login success",
        "user_not_found": "User not found",
        "register_deadline_reached": "Registration deadline reached",
        "register_success": "Registration successful",
        "record_not_found": "Record not found",
        "error_no_permission": "No permission",
        "error_input_invalid": "Invalid input data",
        "error_duplicate": "Duplicate submission",
        "error_id_card": "Invalid ID card",
        "error_phone": "Invalid phone number",
        "error_limit_reached": "Limit reached",
    }
}

def t(key: str) -> str:
    """翻译工具函数"""
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)
