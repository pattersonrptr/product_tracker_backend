from pydantic import BaseModel


class SourceWebsite(BaseModel):
    id: int | None = None
    name: str
    base_url: str
    is_active: bool = True
