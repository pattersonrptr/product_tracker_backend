from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Index,
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


class SourceWebsite(Base):
    """Table to track websites we scrape from"""

    __tablename__ = "source_websites"

    id = Column(Integer, primary_key=True)
    name = Column(
        String(20), unique=True, comment="Website name (e.g., 'OLX', 'Enjoei')"
    )
    base_url = Column(String, comment="Base URL for the website")
    is_active = Column(
        Boolean, default=True, comment="Whether we're currently scraping this site"
    )

    # Relationships
    products = relationship("Product", back_populates="source_website")

    # Indexes
    __table_args__ = (Index("ix_source_website_name", name),)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    product = relationship("Product", back_populates="price_history")

    __table_args__ = (Index("ix_price_history_product", product_id, created_at),)
