from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class ProductFilter(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    current_price: Optional[float] = Field(None, description="Current product price")
