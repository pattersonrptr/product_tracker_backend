from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional, List
import re
from decimal import Decimal


def parse_price(value):
    if isinstance(value, (int, float, Decimal)):
        return float(value)

    if not isinstance(value, str):
        raise ValueError("The value should be a string or a number")

    value = re.sub(r"[^0-9.,]", "", value)
    value = value.replace(",", ".")

    if value.count(".") > 1:
        parts = value.split(".")
        value = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(value)
    except ValueError:
        raise ValueError("Invalid format for float conversion")

class ProductBase(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        validate_default=True,
    )

    @field_validator('price', mode='before')
    @classmethod
    def parse_decimal(cls, value):
        return parse_price(value)

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
        return parse_price(value)

class ProductFilter(BaseModel):
    title: Optional[str] = None
    min_price: Optional[float] = Field(default=None, gt=0)
    max_price: Optional[float] = Field(default=None, gt=0)
    created_after: Optional[date] = None
    created_before: Optional[date] = None

class ProductBulkCreate(BaseModel):
    products: List[ProductCreate]

    @field_validator('products')
    @classmethod
    def check_non_empty_list(cls, value):
        if not value:
            raise ValueError("The products list cannot be empty")
        return value

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
