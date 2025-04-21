from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional


@dataclass
class Product:
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
    last_notified_at: Optional[datetime] = None
    source_metadata: Optional[dict] = None
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)
    id: Optional[int] = None
