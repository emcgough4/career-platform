from app.fallback import resolve_public_profile


def test_resolve_public_profile_uses_fallback_when_db_raises():
    fallback = {"profile": {"full_name": "Jane Doe"}, "projects": []}
    result = resolve_public_profile(db_error=True, fallback_data=fallback)
    assert result["profile"]["full_name"] == "Jane Doe"

