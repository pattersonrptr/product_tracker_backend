from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    url: str
    title: str
    source_website_id: int
    description: Optional[str] = None
    source_product_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    condition: Optional[str] = None
    seller_name: Optional[str] = None
    is_available: bool = True
    image_urls: Optional[str] = None
    source_metadata: Optional[dict] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    current_price: Optional[float] = None
    id: Optional[int] = None
