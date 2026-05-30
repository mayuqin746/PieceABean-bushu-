import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

DATABASE_URL = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

if "tidbcloud.com" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG,
        connect_args={"ssl": {"ssl_mode": "VERIFY_IDENTITY"}},
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=settings.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖注入：每次请求获取一个独立数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
