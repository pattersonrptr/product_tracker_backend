from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class PriceHistory(BaseModel):
    product_id: int
    price: float
    created_at: datetime = datetime.now(timezone.utc)
    id: Optional[int] = None
