from datetime import datetime
from typing import Any
from pydantic import BaseModel, model_validator
from app.core.config import settings


class PatternBase(BaseModel):
    title: str
    description: str | None = None
    category: str = "其他"


class PatternCreate(PatternBase):
    series: str | None = None
    colors: list[str] | None = None
    grid_data: Any = None
    width: int = 0
    height: int = 0


class PatternResponse(PatternBase):
    id: int
    series: str | None = None
    colors: list[str] | None = None
    thumbnail_url: str | None = None
    blueprint_url: str | None = None
    width: int
    height: int
    beads_count: int
    views: int
    likes: int
    owner_id: int | None = None
    is_public: bool = True
    is_favorited: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def prepend_base_url(self):
        base = settings.STATIC_BASE_URL.rstrip("/")
        if self.thumbnail_url and not self.thumbnail_url.startswith("http"):
            self.thumbnail_url = f"{base}{self.thumbnail_url}"
        if self.blueprint_url and not self.blueprint_url.startswith("http"):
            self.blueprint_url = f"{base}{self.blueprint_url}"
        return self


class PatternListResponse(BaseModel):
    total: int
    items: list[PatternResponse]
