from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    id: int | None = None
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
