from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime

class ProductBase(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    price: float = Field(gt=0)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
