import os

from pydantic import BaseModel


def normalize_database_url(url: str) -> str:
    """Point Railway's postgres:// and postgresql:// URLs at the psycopg 3 driver."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./career_platform.db"))
    # Show empty media slots where work is missing (local layout preview only; never set in production).
    preview_slots: bool = os.getenv("PREVIEW_SLOTS") == "1"


settings = Settings()
