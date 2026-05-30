from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    score_ui: Mapped[int] = mapped_column(Integer, nullable=False)
    score_layout: Mapped[int] = mapped_column(Integer, nullable=False)
    score_feature: Mapped[int] = mapped_column(Integer, nullable=False)
    score_ux: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
