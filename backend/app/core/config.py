from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "拼豆 PieceABean"
    DEBUG: bool = True

    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "pieceabean"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    # JWT
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # 静态文件
    STATIC_BASE_URL: str = "http://localhost:8000"

    # 文件上传
    MAX_UPLOAD_SIZE_MB: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
