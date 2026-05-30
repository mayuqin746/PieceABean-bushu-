from datetime import datetime
from typing import Any
from pydantic import BaseModel


class UserPatternSave(BaseModel):
    title: str
    category: str = "其他"
    colors: list[str] | None = None
    grid_data: Any = None
    width: int = 0
    height: int = 0
    beads_count: int = 0


class UserPatternResponse(BaseModel):
    id: int
    user_id: int
    title: str
    category: str
    colors: list[str] | None = None
    grid_data: Any = None
    width: int
    height: int
    beads_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
