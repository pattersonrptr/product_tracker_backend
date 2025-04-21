from typing import Optional

from pydantic import BaseModel


class SourceWebsite(BaseModel):
    name: str
    base_url: str
    is_active: bool = True
    id: Optional[int] = None
