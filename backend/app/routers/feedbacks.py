"""问题反馈接口 —— 用户提交 bug / 建议 / 其他反馈"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedbacks", tags=["问题反馈"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(body: FeedbackCreate, db: Session = Depends(get_db)):
    feedback = Feedback(
        type=body.type,
        content=body.content,
        contact=body.contact,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
