from datetime import time
from typing import Optional, List

from pydantic import BaseModel

from app.interfaces.schemas.source_website_schema import (
    SourceWebsiteRead as SourceWebsiteSchema,
)


class SearchConfigBase(BaseModel):
    search_term: str
    is_active: bool = True
    frequency_days: int = 1
    preferred_time: time = time(0, 0)
    search_metadata: Optional[dict] = None
    source_websites: Optional[List[SourceWebsiteSchema]] = None
    user_id: Optional[int] = None


class SearchConfigCreate(SearchConfigBase):
    pass


class SearchConfigUpdate(SearchConfigBase):
    pass


class SearchConfigInDBBase(SearchConfigBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class SearchConfig(SearchConfigInDBBase):
    pass


class SearchConfigSearchResults(BaseModel):
    results: List[SearchConfig]
