from datetime import datetime
from pydantic import BaseModel, Field


class FAQCreate(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1)
    sort_order: int = Field(default=0)
    is_visible: bool = Field(default=True)


class FAQUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=500)
    answer: str | None = Field(default=None, min_length=1)
    sort_order: int | None = None
    is_visible: bool | None = None


class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    sort_order: int
    is_visible: bool
    created_at: datetime

    model_config = {"from_attributes": True}
