from app.fallback import resolve_public_profile


def test_resolve_public_profile_uses_fallback_when_db_raises():
    fallback = {"profile": {"full_name": "Jane Doe"}, "projects": []}
    result = resolve_public_profile(db_error=True, fallback_data=fallback)
    assert result["profile"]["full_name"] == "Jane Doe"


def test_public_pages_render_snapshot_when_database_has_no_profile(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert "Your Name" in response.text


def test_fallback_snapshot_keeps_required_pages_available(client):
    for route in ("/about", "/resume", "/portfolio", "/contact"):
        assert client.get(route).status_code == 200
