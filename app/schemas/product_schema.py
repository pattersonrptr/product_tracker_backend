from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional, List

class ProductBase(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

    @field_validator('price', mode='before')
    @classmethod
    def parse_decimal(cls, value):
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    title: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, gt=0)

    @field_validator('price', mode='before')
    @classmethod
    def parse_decimal(cls, value):
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)

class ProductFilter(BaseModel):
    title: Optional[str] = None
    min_price: Optional[float] = Field(default=None, gt=0)
    max_price: Optional[float] = Field(default=None, gt=0)
    created_after: Optional[date] = None
    created_before: Optional[date] = None

class ProductBulkCreate(BaseModel):
    products: List[ProductCreate]

class ProductSearch(BaseModel):
    query: str

class ProductStats(BaseModel):
    total_products: int
    average_price: float
    min_price: float
    max_price: float

class ProductPartialResponse(BaseModel):
    id: int
    title: str
    price: float