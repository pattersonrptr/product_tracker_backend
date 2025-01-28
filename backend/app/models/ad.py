from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from ..db.base import Base

class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    price = Column(Float)
    link = Column(String(255), unique=True)
    wishlist = Column(Boolean, default=False)
    last_updated = Column(DateTime)
