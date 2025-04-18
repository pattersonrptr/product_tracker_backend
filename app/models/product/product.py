from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.database import Base


class ProductCondition(str, Enum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Numeric(10, 2))

    # Product code from source website (nullable)
    source_product_code = Column(
        String(50),
        index=True,
        nullable=True,
        comment="Unique identifier from the source website (if available)",
    )

    # Location
    city = Column(String)
    state = Column(String(2))

    # Ad metadata
    condition = Column(SQLAlchemyEnum(ProductCondition), default=ProductCondition.USED)
    seller_type = Column(String(20))  # 'individual' or 'store'
    # TODO: Remove it, use source_website_id
    source = Column(String(20))  # 'olx', 'enjoei', etc
    is_available = Column(Boolean, default=True)

    # Images (URLs separated by commas)
    image_urls = Column(String)

    # Important dates
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    last_notified_at = Column(DateTime)  # For price alerts

    # Improved source tracking (replaces previous 'source' field)
    source_website_id = Column(
        Integer,
        ForeignKey("source_websites.id"),
        index=True,
        comment="Foreign key to source website configuration",
    )
    source_metadata = Column(
        JSON, nullable=True, comment="Additional source-specific data in JSON format"
    )

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    source_website = relationship("SourceWebsite", back_populates="products")
