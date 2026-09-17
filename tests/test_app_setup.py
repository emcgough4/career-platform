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


def test_database_engine_uses_sqlite_thread_compatible_settings():
    from app.db import engine

    assert engine.url.drivername == "sqlite"
    assert engine.pool._creator
