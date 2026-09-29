import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./career_platform.db")


settings = Settings()
