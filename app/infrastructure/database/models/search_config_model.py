from datetime import time, datetime, UTC
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Time,
    ForeignKey,
    JSON,
    Index,
    DateTime,
)
from sqlalchemy.orm import relationship
from .search_config_source_website_model import search_config_source_website

from app.infrastructure.database_config import Base


class SearchConfig(Base):
    __tablename__ = "search_configs"

    id = Column(Integer, primary_key=True)
    search_term = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    frequency_days = Column(Integer, default=1)
    preferred_time = Column(Time, default=time(0, 0))
    search_metadata = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user = relationship("User", back_populates="search_configs")
    search_execution_logs = relationship(
        "SearchExecutionLog", back_populates="search_config"
    )

    source_websites = relationship(
        "SourceWebsite",
        secondary=search_config_source_website,
        back_populates="search_configs",  # <--- CORREÇÃO: Deve ser "search_configs" no SourceWebsite
    )

    __table_args__ = (
        Index("ix_search_term", search_term),
        Index("ix_search_active", is_active),
    )
