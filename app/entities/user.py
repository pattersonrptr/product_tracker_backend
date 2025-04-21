from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional


@dataclass
class User:
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)
    id: Optional[int] = None
