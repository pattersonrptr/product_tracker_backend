from pydantic import BaseModel
from datetime import datetime

class AdBase(BaseModel):
    url: str
    title: str
    price: float

class AdCreate(AdBase):
    pass

class AdResponse(AdBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Isso permite a conversão automática de ORM para Pydantic