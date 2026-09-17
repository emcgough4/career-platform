from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Education, Experience, Profile, Project, Skill
from app.services.fallback_service import load_latest_snapshot


def serialize_profile(profile: Profile | None) -> dict:
    if profile is None:
        return {"profile": {}, "experience": [], "education": [], "skills": [], "projects": []}
    return {
        "profile": {key: getattr(profile, key) for key in (
            "id", "full_name", "headline", "summary", "location", "availability",
            "email", "linkedin_url", "github_url", "portfolio_url", "photo_url",
            "introduction_text",
        )},
        "experience": [
            {key: getattr(item, key) for key in (
                "id", "company_name", "role_title", "start_date", "end_date",
                "is_current", "location", "description", "achievement_summary",
                "skills_used",
            )}
            for item in sorted(profile.experiences, key=lambda item: item.start_date, reverse=True)
        ],
        "education": [
            {key: getattr(item, key) for key in (
                "id", "institution_name", "degree", "field_of_study",
                "start_date", "end_date", "details",
            )}
            for item in profile.education
        ],
        "skills": [
            {key: getattr(item, key) for key in ("id", "name", "category", "proficiency_level", "sort_order")}
            for item in sorted(profile.skills, key=lambda item: item.sort_order)
        ],
        "projects": [
            {
                key: getattr(item, key)
                for key in (
                    "id", "title", "short_description", "long_description", "challenge",
                    "approach", "process", "outcome", "metrics", "status", "featured",
                    "published_at", "cover_image_url", "project_url", "repository_url", "year",
                )
            }
            | {"tags": [tag.label for tag in item.tags]}
            for item in profile.projects
            if item.status == "published"
        ],
    }


def get_public_profile_context(session: Session) -> dict:
    profile = session.scalar(
        select(Profile).options(
            selectinload(Profile.experiences),
            selectinload(Profile.education),
            selectinload(Profile.skills),
            selectinload(Profile.projects).selectinload(Project.tags),
        ).order_by(Profile.id)
    )
    return serialize_profile(profile)


def load_public_profile(session: Session | None) -> tuple[dict, bool]:
    if session is None:
        return load_latest_snapshot(), True
    try:
        return get_public_profile_context(session), False
    except Exception:
        return load_latest_snapshot(), True
