from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field
from app.entities.product import ProductCondition


class ProductBase(BaseModel):
    url: str = Field(..., description="URL do produto na página de origem")
    title: str = Field(..., description="Título do produto")
    description: Optional[str] = Field(None, description="Descrição do produto")
    price: Decimal = Field(..., description="Preço do produto")
    city: str = Field(..., description="Cidade onde o produto está localizado")
    state: str = Field(..., description="Estado onde o produto está localizado (sigla)")
    condition: ProductCondition = Field(
        ProductCondition.USED, description="Condição do produto"
    )
    seller_name: Optional[str] = Field(
        None, description="Tipo de vendedor (individual/loja)"
    )
    source_product_code: Optional[str] = Field(
        None, description="Código do produto no site de origem"
    )
    image_urls: Optional[str] = Field(
        None, description="URLs das imagens do produto (separadas por vírgulas)"
    )
    source_website_id: int = Field(
        ..., description="ID do website de origem (tabela source_websites)"
    )
    source_metadata: Optional[dict] = Field(
        None, description="Metadados específicos da fonte (JSON)"
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    id: Optional[int] = None
    updated_at: Optional[datetime] = None


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductMinimal(BaseModel):
    id: int
    title: str
    price: Decimal
