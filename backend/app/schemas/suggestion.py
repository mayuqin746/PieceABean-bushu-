from datetime import datetime
from pydantic import BaseModel, Field


class SuggestionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    contact: str | None = Field(default=None, max_length=200)


class SuggestionResponse(BaseModel):
    id: int
    title: str
    content: str
    contact: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
