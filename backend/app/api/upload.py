"""
文件上传 API 路由
"""
import os
import uuid
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["文件上传"])

# 允许的文件类型
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/quicktime", "video/x-matroska"
}
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".mp4", ".mov", ".mkv"
}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传图片文件
    - 限制文件类型：jpg/png/gif/webp
    - 限制文件大小：由环境变量控制（默认 5MB）
    - 使用随机文件名存储，防止文件名枚举攻击
    """
    # 校验文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    # 校验文件扩展名
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件扩展名: {ext}")

    # 读取文件内容并检查大小
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE_MB}MB)",
        )

    # 生成安全的随机文件名
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 返回可访问的 URL
    file_url = f"/uploads/{safe_filename}"

    logger.info("文件上传成功: %s (%d bytes)", safe_filename, len(content))

    return {
        "code": 200,
        "message": "上传成功",
        "data": {
            "url": file_url,
            "filename": safe_filename,
            "size": len(content),
        },
    }
