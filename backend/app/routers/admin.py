"""管理后台 —— 图纸上传接口（仅限已登录管理员访问）"""
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from PIL import Image
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.pattern import Pattern
from app.models.user import User
from app.schemas.pattern import PatternResponse

router = APIRouter(prefix="/admin", tags=["管理后台"])

DATA_DIR = Path(r"D:\Desktop\pieceabean-data\patterns")
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
THUMB_SIZE = 600
THUMB_CONTENT_MAX = 480
THUMB_QUALITY = 80


def compress_thumbnail(raw_bytes: bytes, ext: str) -> bytes:
    """统一生成 600x600 正方形白底缩略图：原图等比例缩放 → 主体最大 480x480 → 居中贴到白色画布"""
    img = Image.open(BytesIO(raw_bytes))
    if img.mode == "P":
        img = img.convert("RGBA")
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    scale = THUMB_CONTENT_MAX / max(w, h)
    if scale > 1:
        scale = 1
    new_w = int(w * scale)
    new_h = int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGB", (THUMB_SIZE, THUMB_SIZE), (255, 255, 255))
    offset_x = (THUMB_SIZE - new_w) // 2
    offset_y = (THUMB_SIZE - new_h) // 2
    canvas.paste(img, (offset_x, offset_y))

    output = BytesIO()
    save_format = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
    canvas.save(output, format=save_format, quality=THUMB_QUALITY, optimize=True)
    return output.getvalue()


@router.post("/upload", response_model=PatternResponse, status_code=201)
async def upload_pattern(
    thumbnail_file: UploadFile = File(..., description="封面缩略图"),
    blueprint_file: UploadFile = File(..., description="高清网格图纸"),
    title: str = Form(...),
    category: str = Form(...),
    series: str = Form(default=""),
    colors: str = Form(default="[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 校验两张图的格式
    for f in (thumbnail_file, blueprint_file):
        ext = Path(f.filename).suffix.lower() if f.filename else ".png"
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="仅支持 PNG / JPG / WebP 格式")

    import json
    try:
        colors_list = json.loads(colors) if colors else []
    except json.JSONDecodeError:
        colors_list = []

    thumb_dir = DATA_DIR / "thumbnail"
    full_dir = DATA_DIR / "full"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    full_dir.mkdir(parents=True, exist_ok=True)

    # 缩略图：压缩后存入
    thumb_ext = Path(thumbnail_file.filename).suffix.lower() if thumbnail_file.filename else ".png"
    thumb_raw = await thumbnail_file.read()
    thumb_data = compress_thumbnail(thumb_raw, thumb_ext)
    thumb_name = f"{uuid.uuid4().hex}{thumb_ext}"
    thumb_path = thumb_dir / thumb_name
    with open(thumb_path, "wb") as f:
        f.write(thumb_data)

    # 高清图纸：原样存入
    bp_ext = Path(blueprint_file.filename).suffix.lower() if blueprint_file.filename else ".png"
    bp_raw = await blueprint_file.read()
    bp_size_mb = len(bp_raw) / (1024 * 1024)
    if bp_size_mb > 10:
        raise HTTPException(status_code=413, detail="高清图纸超过 10MB 限制")
    bp_name = f"{uuid.uuid4().hex}{bp_ext}"
    bp_path = full_dir / bp_name
    with open(bp_path, "wb") as f:
        f.write(bp_raw)

    pattern = Pattern(
        title=title,
        category=category,
        series=series or None,
        colors=colors_list or None,
        thumbnail_url=f"/static/patterns/thumbnail/{thumb_name}",
        blueprint_url=f"/static/patterns/full/{bp_name}",
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern
