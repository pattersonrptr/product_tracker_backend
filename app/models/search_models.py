from datetime import time
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Time,
    # ForeignKey,
    JSON,
    Index,
    # CheckConstraint,
)

# from sqlalchemy.orm import relationship
from app.database import Base


class SearchConfig(Base):
    __tablename__ = "search_configs"

    id = Column(Integer, primary_key=True)
    search_term = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    source_websites = Column(JSON)
    frequency_days = Column(Integer, default=1)
    preferred_time = Column(Time, default=time(0, 0))  # Specific parameters per site
    search_metadata = Column(JSON)  # Parâmetros específicos por site
    # user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # If multi-user

    # Relationships
    # user = relationship("User", back_populates="search_configs")

    __table_args__ = (
        Index("ix_search_term", search_term),
        Index("ix_search_active", is_active),
        # CheckConstraint(
        #     "json_array_length(source_websites) > 0",
        #     name="at_least_one_source"
        # ),
    )


# class SearchExecutionLog(Base):
#     __tablename__ = "search_execution_logs"
#     id = Column(Integer, primary_key=True)
#     search_config_id = Column(Integer, ForeignKey('search_configs.id'))
#     timestamp = Column(DateTime, default=datetime.now(UTC))
#     results_count = Column(Integer)
#     status = Column(String(20))
