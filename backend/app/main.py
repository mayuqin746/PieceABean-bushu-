"""拼豆 PieceABean —— FastAPI 应用入口"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.models import User, Pattern, Favorite, UserPattern, Rating  # 注册模型到 Base.metadata
from app.routers import users, patterns, generator
from app.routers.admin import router as admin_router
from app.routers.palette import router as palette_router
from app.routers.ratings import router as ratings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时创建数据库表（开发环境）"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="拼豆图纸在线生成与分享平台",
    lifespan=lifespan,
)

# ─── CORS 跨域配置 ──────────────────────────────────────────────────────────
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

cors_env = os.getenv("BACKEND_CORS_ORIGINS", "")
if cors_env:
    origins.extend(origin.strip() for origin in cors_env.split(",") if origin.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 静态图片 ───────────────────────────────────────────────────────────────
PATTERNS_DIR = Path(r"D:\Desktop\pieceabean-data\patterns")


@app.get("/static/patterns/{subdir}/{filename}")
async def serve_pattern_image(subdir: str, filename: str):
    file_path = (PATTERNS_DIR / subdir / filename).resolve()
    if not str(file_path).startswith(str(PATTERNS_DIR.resolve())):
        raise HTTPException(status_code=403)
    if not file_path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(file_path)

# ─── 注册路由 ──────────────────────────────────────────────────────────────
app.include_router(users.router, prefix="/api/v1")
app.include_router(patterns.router, prefix="/api/v1")
app.include_router(generator.router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(palette_router, prefix="/api/v1")
app.include_router(ratings_router, prefix="/api/v1")


# ─── 根路径健康检查 ─────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": f"欢迎来到 {settings.APP_NAME} API", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
