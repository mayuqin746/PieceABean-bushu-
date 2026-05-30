from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    pattern_id: Mapped[int] = mapped_column(ForeignKey("patterns.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
