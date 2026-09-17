from pydantic import BaseModel


class ProfileSnapshot(BaseModel):
    profile: dict
    experience: list[dict] = []
    education: list[dict] = []
    skills: list[dict] = []
    projects: list[dict] = []
