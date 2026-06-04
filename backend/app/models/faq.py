from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
