"""
MongoDB 数据库连接管理
使用 motor 异步驱动
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """建立 MongoDB 连接，应用启动时调用"""
    global _client, _db
    logger.info("正在连接 MongoDB: %s", settings.MONGODB_URL)
    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    _db = _client[settings.MONGODB_DB_NAME]
    # NOTE: 验证连接是否正常
    await _client.admin.command("ping")
    logger.info("MongoDB 连接成功，数据库: %s", settings.MONGODB_DB_NAME)
    
    # 初始化索引
    await init_indices()

async def init_indices() -> None:
    """初始化数据库索引"""
    try:
        db = get_db()
        # 1. 场馆表：创建地理空间索引 (必须，用于距离排序)
        await db["sign_gyms"].create_index([("location", "2dsphere")])
        
        # 2. 线路表：按场馆 ID 索引
        await db["sign_routes"].create_index([("gym_id", 1)])
        
        # 3. 完攀记录表：按线路和用户索引
        await db["sign_route_attempts"].create_index([("route_id", 1)])
        await db["sign_route_attempts"].create_index([("user_id", 1)])
        
        logger.info("数据库索引初始化完成")
    except Exception as e:
        logger.error("数据库索引初始化失败: %s", str(e))


async def close_db() -> None:
    """关闭 MongoDB 连接，应用停止时调用"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB 连接已关闭")


def get_db() -> AsyncIOMotorDatabase:
    """
    获取数据库实例
    所有 repository 层通过此函数获取 db 引用
    """
    if _db is None:
        raise RuntimeError("数据库未连接，请先调用 connect_db()")
    return _db


def get_collection(name: str):
    """快捷获取集合引用"""
    return get_db()[name]
