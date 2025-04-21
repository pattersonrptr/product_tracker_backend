from datetime import datetime, UTC
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.database_config import Base


class SearchExecutionLog(Base):
    __tablename__ = "search_execution_logs"

    id = Column(Integer, primary_key=True)
    search_config_id = Column(Integer, ForeignKey("search_configs.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(UTC))
    results_count = Column(Integer)
    status = Column(String(20))

    # Relationships
    search_config = relationship("SearchConfig", back_populates="search_execution_logs")
