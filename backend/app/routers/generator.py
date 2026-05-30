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
import random
import base64
import math
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
    grid_data: list[list[str]]
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

    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode == "P":
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _pixelate(img: Image.Image, grid_w: int, grid_h: int) -> Image.Image:
    return img.resize((grid_w, grid_h), Image.Resampling.BOX)


def _extract_grid(img: Image.Image) -> list[list[str]]:
    pixels = img.load()
    w, h = img.size
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = pixels[x, y]
            row.append(f"#{r:02X}{g:02X}{b:02X}")
        grid.append(row)
    return grid


def _cell_pixel_size(grid_size: int) -> int:
    if grid_size <= 30:
        return 20
    elif grid_size <= 60:
        return 12
    else:
        return 8


def _generate_preview(grid_data: list[list[str]], cell_px: int, border_px: int = 1) -> Image.Image:
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


# ─── 色彩空间转换：sRGB ↔ CIELAB (D65) ──────────────────────────────────────

# D65 标准白点
_D65_XN = 0.95047
_D65_YN = 1.00000
_D65_ZN = 1.08883


def _srgb_to_linear(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def _lab_f(t: float) -> float:
    delta = 6.0 / 29.0
    if t > delta ** 3:
        return t ** (1.0 / 3.0)
    return t / (3.0 * delta ** 2) + 4.0 / 29.0


def _lab_f_inv(t: float) -> float:
    delta = 6.0 / 29.0
    if t > delta:
        return t ** 3
    return 3.0 * delta ** 2 * (t - 4.0 / 29.0)


def _rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_lin = _srgb_to_linear(r / 255.0)
    g_lin = _srgb_to_linear(g / 255.0)
    b_lin = _srgb_to_linear(b / 255.0)

    x = r_lin * 0.4124564 + g_lin * 0.3575761 + b_lin * 0.1804375
    y = r_lin * 0.2126729 + g_lin * 0.7151522 + b_lin * 0.0721750
    z = r_lin * 0.0193339 + g_lin * 0.1191920 + b_lin * 0.9503041

    fx = _lab_f(x / _D65_XN)
    fy = _lab_f(y / _D65_YN)
    fz = _lab_f(z / _D65_ZN)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b_lab = 200.0 * (fy - fz)

    return (L, a, b_lab)


def _lab_to_rgb(L: float, a: float, b_lab: float) -> tuple[int, int, int]:
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b_lab / 200.0

    x = _D65_XN * _lab_f_inv(fx)
    y = _D65_YN * _lab_f_inv(fy)
    z = _D65_ZN * _lab_f_inv(fz)

    r_lin = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
    g_lin = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
    b_lin = x *  0.0556434 + y * -0.2040259 + z *  1.0572252

    r = max(0, min(255, round(_linear_to_srgb(r_lin) * 255.0)))
    g = max(0, min(255, round(_linear_to_srgb(g_lin) * 255.0)))
    b = max(0, min(255, round(_linear_to_srgb(b_lin) * 255.0)))

    return (r, g, b)


# ─── K-means 颜色聚类 (感知均匀 Lab 空间) ───────────────────────────────────

def _color_dist(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _kmeans_pp_init(pixels: list[tuple[float, float, float]], k: int) -> list[tuple[float, float, float]]:
    """K-means++ 初始化，让初始聚类中心尽量分散"""
    centroids = [random.choice(pixels)]
    for _ in range(1, k):
        dists = [min(_color_dist(p, c) for c in centroids) for p in pixels]
        total = sum(dists)
        # pick weighted by distance squared
        r = random.random() * total
        acc = 0.0
        for i, d in enumerate(dists):
            acc += d
            if acc >= r:
                centroids.append(pixels[i])
                break
    return centroids


def _kmeans_cluster(
    pixels: list[tuple[float, float, float]], k: int, max_iters: int = 15
) -> tuple[list[tuple[float, float, float]], list[int]]:
    """K-means 聚类 (Lab 空间)，返回 (k 个聚类中心, 每个像素的簇索引)"""
    n = len(pixels)
    if k >= n:
        labels = list(range(n))
        return pixels[:], labels

    centroids = _kmeans_pp_init(pixels, k)
    labels = [0] * n

    for _ in range(max_iters):
        changed = False
        for i, p in enumerate(pixels):
            best_k = 0
            best_d = float('inf')
            for j, c in enumerate(centroids):
                d = _color_dist(p, c)
                if d < best_d:
                    best_d = d
                    best_k = j
            if labels[i] != best_k:
                labels[i] = best_k
                changed = True
        if not changed:
            break
        sums = [[0.0, 0.0, 0.0] for _ in range(k)]
        counts = [0] * k
        for i, p in enumerate(pixels):
            lb = labels[i]
            sums[lb][0] += p[0]
            sums[lb][1] += p[1]
            sums[lb][2] += p[2]
            counts[lb] += 1
        for j in range(k):
            if counts[j] > 0:
                centroids[j] = (
                    sums[j][0] / counts[j],
                    sums[j][1] / counts[j],
                    sums[j][2] / counts[j],
                )

    return centroids, labels


def _quantize(img: Image.Image, color_count: int, algorithm: str = "kmeans") -> Image.Image:
    """降色处理，根据 algorithm 分流至不同实现"""
    w, h = img.size
    total = w * h
    if color_count <= 0 or color_count >= total:
        return img

    if algorithm == "kmeans":
        pixels = img.load()
        all_pixels_rgb = [
            (pixels[x, y][0], pixels[x, y][1], pixels[x, y][2])
            for y in range(h) for x in range(w)
        ]
        all_pixels_lab = [_rgb_to_lab(*p) for p in all_pixels_rgb]

        centroids_lab, labels = _kmeans_cluster(all_pixels_lab, color_count)

        centroids_rgb = [_lab_to_rgb(*c) for c in centroids_lab]

        out = Image.new("RGB", (w, h))
        out_px = out.load()
        for y in range(h):
            for x in range(w):
                idx = y * w + x
                out_px[x, y] = centroids_rgb[labels[idx]]
        return out

    if algorithm == "mediancut":
        return img.quantize(colors=color_count, method=Image.Quantize.MEDIANCUT, kmeans=0).convert("RGB")

    if algorithm == "octree":
        return img.quantize(colors=color_count, method=Image.Quantize.FASTOCTREE).convert("RGB")

    return img


# ─── 路由 ───────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    file: UploadFile = File(..., description="Upload image (JPG/PNG/WebP/BMP)"),
    grid_size: int = Form(29, ge=10, le=100, description="Grid size — target max dimension (default 29)"),
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
        beads_count=grid_w * grid_h,
    )


@router.get("/palette")
async def get_palette():
    """Get color palettes for all three bead brands"""
    return {
        "artkal": PALETTES["artkal"],
        "hama": PALETTES["hama"],
        "perler": PALETTES["perler"],
    }
