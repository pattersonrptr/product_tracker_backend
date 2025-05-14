from pydantic import BaseModel, Field


class SourceWebsiteBase(BaseModel):
    name: str = Field(..., description="Website name (e.g., 'OLX', 'Enjoei')")
    base_url: str = Field(..., description="Base URL of the website")
    is_active: bool = Field(
        True, description="Indicates if we are currently collecting data from this site"
    )


class SourceWebsiteCreate(SourceWebsiteBase):
    pass


class SourceWebsiteRead(SourceWebsiteBase):
    id: int


class SourceWebsiteUpdate(SourceWebsiteBase):
    pass
