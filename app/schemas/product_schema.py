from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    url: str
    title: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Isso permite a conversão automática de ORM para Pydantic