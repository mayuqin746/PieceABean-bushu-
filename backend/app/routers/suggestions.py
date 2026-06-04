"""创意建议接口 —— 用户提交新功能提案"""

from fastapi import APIRouter, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.suggestion import Suggestion
from app.schemas.suggestion import SuggestionCreate, SuggestionResponse

from fastapi import Depends

router = APIRouter(prefix="/suggestions", tags=["创意建议"])


@router.post("/", response_model=SuggestionResponse, status_code=status.HTTP_201_CREATED)
def create_suggestion(body: SuggestionCreate, db: Session = Depends(get_db)):
    suggestion = Suggestion(
        title=body.title,
        content=body.content,
        contact=body.contact,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion
