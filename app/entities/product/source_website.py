from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceWebsite:
    name: str
    base_url: str
    is_active: bool = True
    id: Optional[int] = None
