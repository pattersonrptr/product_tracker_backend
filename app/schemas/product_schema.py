from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from datetime import datetime

class ProductBase(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

    @field_validator('price', mode='before')
    @classmethod
    def parse_brazilian_decimal(cls, value):
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
