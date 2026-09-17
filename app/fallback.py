from app.services.fallback_service import load_latest_snapshot


def resolve_public_profile(db_error: bool, fallback_data: dict | None = None) -> dict:
    if db_error:
        return fallback_data if fallback_data is not None else load_latest_snapshot()
    return fallback_data or load_latest_snapshot()
