from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class FeedbackCreate(BaseModel):
    type: Literal["bug", "suggestion", "other"]
    content: str = Field(min_length=1)
    contact: str | None = Field(default=None, max_length=200)


class FeedbackResponse(BaseModel):
    id: int
    type: str
    content: str
    contact: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
