"""
FastAPI 应用主入口
- 挂载所有路由
- 配置 CORS、限流、静态文件
- 管理数据库生命周期
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import connect_db, close_db
from app.api import user, register, payment, admin, upload, gym
from app.utils.i18n import set_lang

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 限流器
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在启动应用...")
    await connect_db()
    from app.repository.user_repo import ensure_admin_exists
    from app.repository.gym_repo import init_gym_indices
    await ensure_admin_exists()
    await init_gym_indices()
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("应用启动完成，服务端口: %s", settings.SERVER_PORT)
    yield
    logger.info("正在关闭应用...")
    await close_db()


app = FastAPI(
    title="赛事报名系统 API",
    description="赛事报名微信小程序后端服务",
    version="2.0.0",
    lifespan=lifespan,
)

# 限流中间件
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 多语言中间件
@app.middleware("http")
async def i18n_middleware(request: Request, call_next):
    # 优先从自定义头获取，其次从 Accept-Language 获取
    lang = request.headers.get("x-lang") or request.headers.get("accept-language", "zh")
    set_lang(lang)
    response = await call_next(request)
    return response

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(user.router)
app.include_router(register.router)
app.include_router(payment.router)
app.include_router(admin.router)
app.include_router(upload.router)
app.include_router(gym.router)

# 静态文件（上传的图片）
upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.get("/")
async def root():
    """健康检查"""
    return {"code": 200, "message": "赛事报名系统 API 服务运行中", "version": "2.0.0"}


@app.get("/api/health")
async def health():
    """健康检查接口"""
    return {"code": 200, "message": "ok"}


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("未捕获异常: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
