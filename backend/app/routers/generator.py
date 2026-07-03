"""
工作台 —— 图片上传与拼豆图纸生成接口

该模块负责：
1. 接收用户上传的原始图片，一步完成上传+生成（全程内存处理，不落盘）
2. K-means 颜色聚类 + Artkal 色板映射，将图片量化为指定数量的拼豆颜色
3. 生成带格子边框的预览 PNG（base64 返回）
4. 提供品牌色板数据供前端本地匹配
"""

import io
import uuid
import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from PIL import Image, ImageDraw

from app.core.config import settings
from app.palette import PALETTES

router = APIRouter(prefix="/generator", tags=["工作台"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


class GenerateResponse(BaseModel):
    task_id: str
    grid_data: list[list[str | None]]
    preview_base64: str
    width: int
    height: int
    beads_count: int


# ─── 辅助函数 ───────────────────────────────────────────────────────────────

def _validate_file(filename: str | None, file_size: int | None) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail="File name cannot be empty")
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported format, only JPG/PNG/WebP/BMP")
    size_mb = file_size / (1024 * 1024) if file_size else 0
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")


def _open_and_prepare_image(data: bytes) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot decode image file")

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def _pixelate(img: Image.Image, grid_w: int, grid_h: int) -> Image.Image:
    return img.resize((grid_w, grid_h), Image.Resampling.LANCZOS)


def _extract_grid(img: Image.Image) -> list[list[str | None]]:
    pixels = img.load()
    w, h = img.size
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, a = pixels[x, y]
            row.append(None if a < 128 else f"#{r:02X}{g:02X}{b:02X}")
        grid.append(row)
    return grid


def _cell_pixel_size(grid_size: int) -> int:
    if grid_size <= 30:
        return 20
    elif grid_size <= 60:
        return 12
    else:
        return 8


def _generate_preview(grid_data: list[list[str | None]], cell_px: int, border_px: int = 1) -> Image.Image:
    grid_h = len(grid_data)
    grid_w = len(grid_data[0]) if grid_data else 0
    total_w = grid_w * (cell_px + border_px) + border_px
    total_h = grid_h * (cell_px + border_px) + border_px
    bg_color = (200, 200, 200)
    preview = Image.new("RGB", (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(preview)

    for y in range(grid_h):
        for x in range(grid_w):
            hex_color = grid_data[y][x]
            if hex_color is None:
                continue
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            left = x * (cell_px + border_px) + border_px
            top = y * (cell_px + border_px) + border_px
            draw.rectangle(
                [left, top, left + cell_px - 1, top + cell_px - 1],
                fill=(r, g, b),
            )
    return preview


def _preview_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _quantize(img: Image.Image, color_count: int, algorithm: str = "kmeans") -> Image.Image:
    """降色处理（基于 Pillow C 实现，毫秒级完成）"""
    w, h = img.size
    total = w * h
    if color_count <= 0 or color_count >= total:
        return img

    alpha = img.getchannel("A")
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(img.convert("RGB"), mask=alpha)

    if algorithm == "kmeans":
        quantized = rgb.convert("P", palette=Image.ADAPTIVE, colors=color_count).convert("RGBA")
        quantized.putalpha(alpha)
        return quantized

    if algorithm == "mediancut":
        quantized = rgb.quantize(colors=color_count, method=Image.Quantize.MEDIANCUT, kmeans=0).convert("RGBA")
        quantized.putalpha(alpha)
        return quantized

    if algorithm == "octree":
        quantized = rgb.quantize(colors=color_count, method=Image.Quantize.FASTOCTREE).convert("RGBA")
        quantized.putalpha(alpha)
        return quantized

    return img


# ─── 路由 ───────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    file: UploadFile = File(..., description="Upload image (JPG/PNG/WebP/BMP)"),
    grid_size: int = Form(29, ge=10, le=200, description="Grid size — target max dimension (default 29)"),
    color_count: int = Form(0, ge=0, le=64, description="Target color count (0 = no clustering)"),
    algorithm: str = Form("kmeans", description="Color reduction algorithm: kmeans|mediancut|octree"),
):
    """Upload image → pixelate → quantize → bead pattern"""
    if algorithm not in ("kmeans", "mediancut", "octree"):
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm}")
    _validate_file(file.filename, file.size)
    data = await file.read()

    img = _open_and_prepare_image(data)
    orig_w, orig_h = img.size

    if orig_w >= orig_h:
        grid_w = grid_size
        grid_h = max(1, round(grid_size * orig_h / orig_w))
    else:
        grid_h = grid_size
        grid_w = max(1, round(grid_size * orig_w / orig_h))

    pixelated = _pixelate(img, grid_w, grid_h)

    if color_count > 0:
        pixelated = _quantize(pixelated, color_count, algorithm)

    grid_data = _extract_grid(pixelated)

    cell_px = _cell_pixel_size(grid_size)
    preview = _generate_preview(grid_data, cell_px)

    task_id = uuid.uuid4().hex
    preview_base64 = _preview_to_base64(preview)

    return GenerateResponse(
        task_id=task_id,
        grid_data=grid_data,
        preview_base64=preview_base64,
        width=grid_w,
        height=grid_h,
        beads_count=sum(1 for row in grid_data for cell in row if cell is not None),
    )


@router.get("/palette")
async def get_palette():
    """Get color palettes for all three bead brands"""
    return {
        "artkal": PALETTES["artkal"],
        "hama": PALETTES["hama"],
        "perler": PALETTES["perler"],
    }
