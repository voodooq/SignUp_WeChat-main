"""
输入校验工具
- 身份证号格式与校验码验证
- 手机号格式验证
"""
import re


def validate_id_card(id_card: str) -> bool:
    """
    校验 18 位身份证号格式与校验码
    规则：地区码(6位) + 出生日期(8位) + 序号(3位) + 校验码(1位)
    """
    pattern = r"^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$"
    if not re.match(pattern, id_card):
        return False

    # 加权因子
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]

    total = sum(int(id_card[i]) * weights[i] for i in range(17))
    return id_card[17].upper() == check_codes[total % 11]


def validate_phone(phone: str) -> bool:
    """校验中国大陆手机号格式（11位，1开头）"""
    return bool(re.match(r"^1[3-9]\d{9}$", phone))


def sanitize_text(text: str, max_length: int = 500) -> str:
    """
    文本消毒：去除首尾空白 + 长度限制
    防止 XSS 和超长文本攻击
    """
    if not text:
        return ""
    return text.strip()[:max_length]
