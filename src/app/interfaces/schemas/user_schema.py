from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserSearchResults(BaseModel):
    results: List[User]
