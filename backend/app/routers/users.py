from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.pattern import Pattern
from app.models.favorite import Favorite
from app.models.user_pattern import UserPattern
from app.schemas.user import UserRegister, UserLogin, UserUpdate, UserResponse, UserProfile, Token, TokenWithUser
from app.schemas.pattern import PatternResponse
from app.schemas.user_pattern import UserPatternSave, UserPatternResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenWithUser)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(user.id)
    return TokenWithUser(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patterns_count = db.query(UserPattern).filter(UserPattern.user_id == current_user.id).count()
    favorites_count = db.query(Favorite).filter(Favorite.user_id == current_user.id).count()
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        created_at=current_user.created_at,
        patterns_count=patterns_count,
        favorites_count=favorites_count,
    )


@router.patch("/me", response_model=UserResponse)
def update_my_profile(body: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.username is not None and body.username != current_user.username:
        existing = db.query(User).filter(User.username == body.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        current_user.username = body.username
    if body.bio is not None:
        current_user.bio = body.bio
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/patterns", response_model=list[UserPatternResponse])
def get_my_patterns(
    category: str | None = Query(None, description="分类筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(UserPattern).filter(UserPattern.user_id == current_user.id)
    if category and category != "全部":
        query = query.filter(UserPattern.category == category)
    patterns = query.order_by(UserPattern.created_at.desc()).all()
    return patterns


@router.delete("/me/patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_pattern(
    pattern_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pattern = (
        db.query(UserPattern)
        .filter(UserPattern.id == pattern_id, UserPattern.user_id == current_user.id)
        .first()
    )
    if not pattern:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(pattern)
    db.commit()


@router.get("/me/favorites", response_model=list[PatternResponse])
def get_my_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patterns = (
        db.query(Pattern)
        .join(Favorite, Favorite.pattern_id == Pattern.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    for p in patterns:
        p.is_favorited = True
    return patterns


@router.post("/me/patterns", response_model=UserPatternResponse, status_code=status.HTTP_201_CREATED)
def save_my_pattern(
    body: UserPatternSave,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pattern = UserPattern(
        title=body.title,
        category=body.category,
        colors=body.colors,
        grid_data=body.grid_data,
        width=body.width,
        height=body.height,
        beads_count=body.beads_count,
        user_id=current_user.id,
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern
