from datetime import time
from typing import List, Optional

from pydantic import BaseModel

from app.entities.source_website import SourceWebsite as SourceWebsiteEntity


class SearchConfig(BaseModel):
    search_term: str
    is_active: bool = True
    frequency_days: int = 1
    preferred_time: time = time(0, 0)
    search_metadata: Optional[dict] = None
    source_websites: Optional[List[SourceWebsiteEntity]] = None
    user_id: Optional[int] = None
    id: Optional[int] = None
