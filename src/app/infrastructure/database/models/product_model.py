from datetime import timezone, datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from src.app.infrastructure.database_config import Base


class ProductCondition(str, Enum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"
    UNDETERMINED = "undetermined"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String)

    # Product code from source website (nullable) - Example: source + '-' + the product code in website = olx-1365326779)
    source_product_code = Column(
        String(50),
        index=True,
        nullable=True,
        comment="Unique identifier from the source website (if available)",
    )

    # Location
    city = Column(String)
    state = Column(String)

    # Ad metadata
    condition = Column(
        SQLAlchemyEnum(ProductCondition), default=ProductCondition.UNDETERMINED
    )
    seller_name = Column(String(255))
    is_available = Column(Boolean, default=True)

    # Images (URLs separated by commas)
    image_urls = Column(String)

    # Important dates
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

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
    price_history = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )
    source_website = relationship("SourceWebsite", back_populates="products")
