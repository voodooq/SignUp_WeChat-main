"""
应用配置管理
所有敏感配置从环境变量读取，禁止硬编码
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """全局配置，自动从 .env / 环境变量加载"""

    # MongoDB
    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DB_NAME: str = "sign_wechat"

    # 服务
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # 微信小程序
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""

    # 微信支付（第二阶段）
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""
    WECHAT_SUBSCRIBE_TEMPLATE_ID: str = ""

    # 安全密钥
    AES_SECRET_KEY: str = "change_me_in_production_32chars!"
    JWT_SECRET_KEY: str = "change_me_jwt_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 168  # 7 天

    # 模拟支付
    ENABLE_MOCK_PAY: bool = True

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_OPENIDS: List[str] = []  # 显式授权的管理员微信 OpenID 列表

    # CORS
    CORS_ORIGINS: str = "*"

    @property
    def cors_origin_list(self) -> List[str]:
        """解析 CORS 允许域名列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """文件上传大小上限（字节）"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# NOTE: 全局单例，所有模块通过 from app.config import settings 引用
settings = Settings()
