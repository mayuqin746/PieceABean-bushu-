from datetime import datetime
from sqlalchemy import String, Integer, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserPattern(Base):
    __tablename__ = "user_patterns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="其他")
    colors: Mapped[list | None] = mapped_column(JSON, default=None)
    grid_data: Mapped[list | None] = mapped_column(JSON, default=None)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    beads_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
