from datetime import UTC, datetime

from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from src.app.infrastructure.database_config import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    product = relationship("Product", back_populates="price_history")

    __table_args__ = (Index("ix_price_history_product", product_id, created_at),)
