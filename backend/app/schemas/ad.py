from pydantic import BaseModel

class AdBase(BaseModel):
    title: str
    price: float
    link: str

class AdCreate(AdBase):
    pass

class Ad(AdBase):
    id: int
    wishlist: bool

    class Config:
        orm_mode = True
