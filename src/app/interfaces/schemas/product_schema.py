from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.app.infrastructure.database.models.product_model import ProductCondition


class ProductBase(BaseModel):
    url: str = Field(..., description="Product URL")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    source_product_code: Optional[str] = Field(
        None, description="Product code on the source website"
    )
    city: str = Field(..., description="Product city")
    state: str = Field(..., description="Product state")
    condition: Optional[ProductCondition] = Field(
        ProductCondition.USED,
        description="Product condition",
    )
    seller_name: Optional[str] = Field(None, description="Seller name")
    is_available: bool = Field(True, description="Product availability")
    image_urls: Optional[str] = Field(None, description="Image URLs (comma-separated)")
    source_website_id: int = Field(..., description="Source website ID")
    source_metadata: Optional[dict] = Field(
        None, description="Source-specific metadata"
    )


class ProductCreate(ProductBase):
    price: float = Field(..., description="Initial product price")


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    current_price: Optional[float] = Field(None, description="Current product price")


class ProductUpdate(ProductBase):
    price: Optional[float] = Field(None, description="New product price (for update)")


class ProductMinimal(BaseModel):
    id: int
    title: str
    url: str
    current_price: Optional[float] = Field(None, description="Current product price")
