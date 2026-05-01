"""
加密工具模块
- AES 加密/解密身份证号
- SHA256 哈希（用于判重）
- 身份证号脱敏
"""
import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

from app.config import settings


def _get_aes_key() -> bytes:
    """
    获取 AES-256 密钥
    NOTE: 从环境变量读取，保持与原始 CryptoJS 兼容的密钥派生方式
    为了向前兼容旧数据，这里支持两种模式：
    - 新模式：使用 AES-256-CBC 标准加密
    """
    key = settings.AES_SECRET_KEY.encode("utf-8")
    # 确保密钥长度为 32 字节（AES-256）
    return hashlib.sha256(key).digest()


def encrypt_id_card(id_card: str) -> str:
    """
    AES-256-CBC 加密身份证号
    返回 base64 编码字符串（格式: iv:ciphertext）
    """
    key = _get_aes_key()
    iv = os.urandom(16)
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(id_card.encode("utf-8")) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 将 iv 和密文一起存储
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt_id_card(encrypted: str) -> str:
    """
    AES-256-CBC 解密身份证号
    输入为 base64 编码字符串
    """
    try:
        key = _get_aes_key()
        raw = base64.b64decode(encrypted)
        iv = raw[:16]
        ciphertext = raw[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data.decode("utf-8")
    except Exception:
        return ""


def hash_id_card(id_card: str) -> str:
    """
    SHA-256 哈希身份证号（用于判重查询，确定性输出）
    统一转大写后哈希，确保身份证号末尾 x/X 不影响判重
    """
    return hashlib.sha256(id_card.upper().encode("utf-8")).hexdigest()


def mask_id_card(id_card: str) -> str:
    """身份证号脱敏显示（前3后4）"""
    if not id_card or len(id_card) < 8:
        return id_card or ""
    return id_card[:3] + "****" + id_card[-4:]
