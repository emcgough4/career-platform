import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./career_platform.db")
    # Show empty media slots where work is missing (local layout preview only; never set in production).
    preview_slots: bool = os.getenv("PREVIEW_SLOTS") == "1"


settings = Settings()
