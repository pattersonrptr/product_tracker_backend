from typing import Optional
from pydantic import BaseModel, Field


class SourceWebsiteBase(BaseModel):
    name: str = Field(..., description="Nome do website (e.g., 'OLX', 'Enjoei')")
    base_url: str = Field(..., description="URL base do website")
    is_active: bool = Field(
        True, description="Indica se estamos atualmente coletando dados deste site"
    )


class SourceWebsiteCreate(SourceWebsiteBase):
    pass


class SourceWebsiteRead(SourceWebsiteBase):
    id: int


class SourceWebsiteUpdate(SourceWebsiteBase):
    id: Optional[int] = None
