from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
