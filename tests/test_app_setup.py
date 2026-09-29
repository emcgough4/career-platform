from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_route_renders_without_crashing():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200


def test_root_route_redirects_to_about():
    client = TestClient(app)

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/about"


def test_database_engine_uses_sqlite_thread_compatible_settings():
    from app.db import engine

    assert engine.url.drivername == "sqlite"
    assert engine.pool._creator
