from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingResponse, RatingStats
from app.api.deps import get_current_user, get_optional_user

router = APIRouter(prefix="/ratings", tags=["打分"])


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_rating(
    body: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Rating).filter(Rating.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已经提交过评分了，感谢反馈！")

    rating = Rating(
        user_id=current_user.id,
        score_ui=body.score_ui,
        score_layout=body.score_layout,
        score_feature=body.score_feature,
        score_ux=body.score_ux,
        comment=body.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/stats", response_model=RatingStats)
def get_rating_stats(db: Session = Depends(get_db)):
    count = db.query(Rating).count()
    if count == 0:
        return RatingStats(count=0, avg_ui=0, avg_layout=0, avg_feature=0, avg_ux=0, avg_overall=0)

    result = db.query(
        func.count(Rating.id),
        func.avg(Rating.score_ui),
        func.avg(Rating.score_layout),
        func.avg(Rating.score_feature),
        func.avg(Rating.score_ux),
    ).first()

    c, ui, layout, feat, ux = result
    overall = round((float(ui or 0) + float(layout or 0) + float(feat or 0) + float(ux or 0)) / 4, 1)
    return RatingStats(
        count=c or 0,
        avg_ui=round(float(ui or 0), 1),
        avg_layout=round(float(layout or 0), 1),
        avg_feature=round(float(feat or 0), 1),
        avg_ux=round(float(ux or 0), 1),
        avg_overall=overall,
    )
