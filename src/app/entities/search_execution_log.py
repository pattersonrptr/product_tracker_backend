from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class SearchExecutionLog(BaseModel):
    search_config_id: int
    timestamp: datetime = datetime.now(timezone.utc)
    results_count: Optional[int] = None
    status: Optional[str] = None
    id: Optional[int] = None
