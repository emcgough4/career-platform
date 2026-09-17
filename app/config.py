from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = "sqlite:///./career_platform.db"


settings = Settings()
