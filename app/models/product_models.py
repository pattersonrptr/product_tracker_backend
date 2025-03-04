from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.database import Base

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
