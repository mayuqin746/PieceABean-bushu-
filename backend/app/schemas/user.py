from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    patterns_count: int = 0
    favorites_count: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithUser(Token):
    user: UserResponse
