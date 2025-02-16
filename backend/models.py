from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Text, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ad(Base):
    __tablename__ = 'ad'
    
    id = Column(Integer, primary_key=True)    # TODO id = Column(Integer, primary_key=True, index=True)
    url = Column(Text())    # TODO url = Column(String, unique=True, index=True)
    title = Column(String(50))   # TODO pode ser só String
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
