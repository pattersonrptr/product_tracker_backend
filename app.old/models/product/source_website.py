from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base


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
