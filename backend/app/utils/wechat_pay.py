"""
微信支付工具模块（第二阶段实现）
- MD5 签名
- XML 序列化/反序列化
- 统一下单/查询订单
"""
import hashlib
import re
from typing import Dict


def md5_sign(params: Dict[str, str], api_key: str) -> str:
    """微信支付 MD5 签名"""
    sorted_keys = sorted(params.keys())
    parts = []
    for key in sorted_keys:
        val = params.get(key)
        if val is not None and val != "" and key != "sign":
            parts.append(f"{key}={val}")
    string_a = "&".join(parts) + f"&key={api_key}"
    return hashlib.md5(string_a.encode("utf-8")).hexdigest().upper()


def to_xml(data: Dict[str, str]) -> str:
    """字典转微信支付 XML 格式"""
    items = "".join(f"<{k}><![CDATA[{v}]]></{k}>" for k, v in data.items())
    return f"<xml>{items}</xml>"


def parse_xml(xml_str: str) -> Dict[str, str]:
    """解析微信支付返回的 XML"""
    result: Dict[str, str] = {}
    # 匹配 CDATA 格式
    for match in re.finditer(r"<(\w+)><!\[CDATA\[(.*?)\]\]></\1>", xml_str):
        result[match.group(1)] = match.group(2)
    # 匹配非 CDATA 格式
    for match in re.finditer(r"<(\w+)>([^<]+)</\1>", xml_str):
        if match.group(1) not in result:
            result[match.group(1)] = match.group(2)
    return result
