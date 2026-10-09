import json
from pathlib import Path

from app.main import app

CONFIG = json.loads((Path(__file__).resolve().parents[1] / "railway.json").read_text())


def test_start_command_listens_on_railway_port_behind_proxy():
    start = CONFIG["deploy"]["startCommand"]
    assert "uvicorn app.main:app" in start
    assert "--host 0.0.0.0" in start
    assert "$PORT" in start
    # Railway's proxy terminates HTTPS; trusting its headers keeps request.base_url on https://.
    assert "--forwarded-allow-ips=*" in start


def test_migrations_run_before_each_deploy():
    assert CONFIG["deploy"]["preDeployCommand"] == ["alembic upgrade head"]


def test_healthcheck_path_is_a_real_route():
    assert CONFIG["deploy"]["healthcheckPath"] in {getattr(route, "path", None) for route in app.routes}


def test_railpack_builds_with_the_same_start_command():
    # Railpack's build step refuses to run without its own start command; railway.json's isn't passed to it.
    railpack = json.loads((Path(__file__).resolve().parents[1] / "railpack.json").read_text())
    assert railpack["deploy"]["startCommand"] == CONFIG["deploy"]["startCommand"]
