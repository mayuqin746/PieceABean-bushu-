from datetime import datetime
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    score_ui: int = Field(ge=1, le=5)
    score_layout: int = Field(ge=1, le=5)
    score_feature: int = Field(ge=1, le=5)
    score_ux: int = Field(ge=1, le=5)
    comment: str | None = None


class RatingResponse(BaseModel):
    id: int
    user_id: int
    score_ui: int
    score_layout: int
    score_feature: int
    score_ux: int
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RatingStats(BaseModel):
    count: int
    avg_ui: float
    avg_layout: float
    avg_feature: float
    avg_ux: float
    avg_overall: float
