from datetime import datetime, UTC
from typing import Optional

from pydantic import BaseModel


class PriceHistory(BaseModel):
    product_id: int
    price: float
    created_at: datetime = datetime.now(UTC)
    id: Optional[int] = None
