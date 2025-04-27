from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.infrastructure.database.models.product_model import ProductCondition


class ProductBase(BaseModel):
    url: str = Field(..., description="URL do produto")
    title: str = Field(..., description="Título do produto")
    description: Optional[str] = Field(None, description="Descrição do produto")
    source_product_code: Optional[str] = Field(
        None, description="Código do produto no site de origem"
    )
    city: str = Field(..., description="Cidade do produto")
    state: str = Field(..., description="Estado do produto")
    condition: Optional[ProductCondition] = Field(
        ProductCondition.USED,
        description="Condição do produto",
    )
    seller_name: Optional[str] = Field(None, description="Nome do vendedor")
    is_available: bool = Field(True, description="Disponibilidade do produto")
    image_urls: Optional[str] = Field(
        None, description="URLs das imagens (separadas por vírgulas)"
    )
    source_website_id: int = Field(..., description="ID do site de origem")
    source_metadata: Optional[dict] = Field(
        None, description="Metadados específicos da fonte"
    )


class ProductCreate(ProductBase):
    price: float = Field(..., description="Preço inicial do produto")


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    current_price: Optional[float] = Field(None, description="Preço atual do produto")


class ProductUpdate(ProductBase):
    price: Optional[float] = Field(
        None, description="Novo preço do produto (para atualização)"
    )


class ProductMinimal(BaseModel):
    id: int
    title: str
    url: str
    current_price: Optional[float] = Field(None, description="Preço atual do produto")
