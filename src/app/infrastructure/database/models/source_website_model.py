from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .search_config_source_website_model import search_config_source_website

from src.app.infrastructure.database_config import Base


class SourceWebsite(Base):
    __tablename__ = "source_websites"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    base_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    products = relationship("Product", back_populates="source_website")
    search_configs = relationship(
        "SearchConfig",
        secondary=search_config_source_website,
        back_populates="source_websites",
    )
