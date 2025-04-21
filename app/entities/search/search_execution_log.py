from datetime import datetime, UTC
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchExecutionLog:
    search_config_id: int
    timestamp: datetime = datetime.now(UTC)
    results_count: Optional[int] = None
    status: Optional[str] = None
    id: Optional[int] = None
