from pydantic import BaseModel


class TokenPayload(BaseModel):
    token: str
