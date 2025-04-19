from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class PriceHistoryBase(BaseModel):
    product_id: int = Field(..., description="ID do produto associado")
    price: Decimal = Field(..., description="Preço registrado")


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistoryRead(PriceHistoryBase):
    id: int
    created_at: datetime


class PriceHistoryUpdate(PriceHistoryBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
