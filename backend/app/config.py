
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./olx.db"
    SENDGRID_API_KEY: str = None

    class Config:
        env_file = ".env"

settings = Settings()
