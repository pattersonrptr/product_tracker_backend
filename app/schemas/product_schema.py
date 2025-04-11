import re
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


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


class JSONAPIBase(BaseModel):
    id: Optional[int] = None
    type: str

    class Config:
        orm_mode = True


class ProductAttributes(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

    @field_validator("price", mode="before")
    @classmethod
    def parse_decimal(cls, value):
        return parse_price(value)


class ProductCreate(JSONAPIBase):
    type: str = "products"
    attributes: ProductAttributes

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data.pop("type", None)  # Removing type field - will use this later
        attributes = data.pop("attributes", {})  # Same here
        data.update(attributes)
        return data


class ProductResponse(BaseModel):
    id: int
    title: str
    url: str
    price: float
    type: str = "products"
    created_at: str
    updated_at: Optional[str]

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_str(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()  # Convert datetime to ISO 8601 string
        return value

    class Config:
        orm_mode = True
        from_attributes = True


class ProductUpdate(BaseModel):
    attributes: Optional[ProductAttributes] = None

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if "attributes" in data and "url" in data["attributes"]:
            # Converte HttpUrl para string
            data["attributes"]["url"] = str(data["attributes"]["url"])
        return data


class ProductFilter(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    min_price: Optional[float] = Field(default=None, gt=0)
    max_price: Optional[float] = Field(default=None, gt=0)
    created_after: Optional[date] = None
    created_before: Optional[date] = None
    updated_after: Optional[date] = None
    updated_before: Optional[date] = None


class ProductBulkCreate(BaseModel):
    data: List[ProductCreate]

    @field_validator("data")
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
    type: str = "products"
    title: str
    price: float

    class Config:
        orm_mode = True
        from_attributes = True
