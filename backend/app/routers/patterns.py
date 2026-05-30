from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.database import get_db
from app.models.pattern import Pattern
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.pattern import PatternCreate, PatternResponse, PatternListResponse
from app.api.deps import get_current_user, get_optional_user

router = APIRouter(prefix="/patterns", tags=["图鉴"])


@router.get("/categories")
def list_categories():
    return {"categories": ["全部", "动漫/IP", "萌宠动物", "美食饮品", "生活日常", "明星应援", "其他"]}


@router.get("/", response_model=PatternListResponse)
def list_patterns(
    category: str | None = Query(None, description="主题筛选"),
    series: str | None = Query(None, description="系列筛选"),
    color: str | None = Query(None, description="色系筛选，多色系用逗号分隔"),
    keyword: str | None = Query(None, description="关键词搜索，模糊匹配标题"),
    sort: str = Query("created_at", description="排序字段: created_at, likes, views"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    query = db.query(Pattern)

    # 关键词：模糊匹配标题
    if keyword:
        query = query.filter(Pattern.title.like(f"%{keyword}%"))

    # 主题：非"全部"时精确匹配
    if category and category != "全部":
        query = query.filter(Pattern.category == category)

    # 系列：非"全部"时精确匹配
    if series and series != "全部":
        query = query.filter(Pattern.series == series)

    # 色系：多选 OR 逻辑，MySQL JSON_CONTAINS
    if color and color != "全部色系":
        color_list = [c.strip() for c in color.split(",") if c.strip()]
        if color_list:
            color_filters = [
                func.json_contains(Pattern.colors, f'"{c}"')
                for c in color_list
            ]
            query = query.filter(or_(*color_filters))

    sort_col = getattr(Pattern, sort, Pattern.created_at)
    total = query.count()
    items = query.order_by(sort_col.desc()).offset((page - 1) * page_size).limit(page_size).all()
    if current_user:
        fav_ids = {
            f.pattern_id for f in db.query(Favorite.pattern_id).filter(Favorite.user_id == current_user.id).all()
        }
        for item in items:
            item.is_favorited = item.id in fav_ids
    return PatternListResponse(total=total, items=items)


@router.get("/random", response_model=PatternResponse)
def get_random_pattern(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    pattern = db.query(Pattern).order_by(func.random()).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="图库为空")
    if current_user:
        fav = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.pattern_id == pattern.id,
        ).first()
        pattern.is_favorited = fav is not None
    return pattern


@router.get("/{pattern_id}", response_model=PatternResponse)
def get_pattern(
    pattern_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="图纸不存在")
    pattern.views = Pattern.views + 1
    db.commit()
    db.refresh(pattern)
    if current_user:
        fav = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.pattern_id == pattern_id,
        ).first()
        pattern.is_favorited = fav is not None
    return pattern


@router.post("/", response_model=PatternResponse, status_code=201)
def create_pattern(body: PatternCreate, db: Session = Depends(get_db)):
    pattern = Pattern(**body.model_dump())
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


@router.post("/{pattern_id}/favorite")
def toggle_favorite(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="图纸不存在")
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.pattern_id == pattern_id,
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False}
    db.add(Favorite(user_id=current_user.id, pattern_id=pattern_id))
    db.commit()
    return {"favorited": True}
