from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Pattern(Base):
    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="其他")
    series: Mapped[str | None] = mapped_column(String(100), default=None)
    colors: Mapped[dict | None] = mapped_column(JSON, default=None)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), default=None)
    blueprint_url: Mapped[str | None] = mapped_column(String(512), default=None)
    grid_data: Mapped[dict | None] = mapped_column(JSON, default=None)
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    beads_count: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="patterns")
    favorited_by: Mapped[list["User"]] = relationship(
        "User", secondary="favorites", back_populates="favorites"
    )
