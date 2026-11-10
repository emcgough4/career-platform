import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY = REPO_ROOT / "deploy" / "aws"


def read(name: str) -> str:
    return (DEPLOY / name).read_text()


def test_unit_runs_uvicorn_on_loopback_without_trusting_all_proxies():
    unit = read("career-platform.service")
    exec_start = next(line for line in unit.splitlines() if line.startswith("ExecStart="))
    assert "/opt/career-platform/.venv/bin/uvicorn app.main:app" in exec_start
    assert "--host 127.0.0.1" in exec_start and "--port 8000" in exec_start and "--workers 2" in exec_start
    # Unlike Railway, nginx on the same machine is the only proxy, and uvicorn trusts 127.0.0.1 by default.
    assert "0.0.0.0" not in unit and "--forwarded-allow-ips" not in unit


def test_unit_runs_as_app_user_with_app_env():
    unit = read("career-platform.service")
    for line in ["User=career-app", "Group=career-app", "WorkingDirectory=/opt/career-platform",
                 "EnvironmentFile=/etc/career-platform/app.env", "Restart=always", "WantedBy=multi-user.target"]:
        assert line in unit.splitlines()
    # The owner credentials are for migrations only; the running app never sees them.
    assert "migrate.env" not in unit


def test_nginx_proxies_to_loopback_for_test_and_real_names():
    conf = read("nginx-career-platform.conf")
    assert "listen 80 default_server;" in conf
    assert "server_name aws.elliemcgough.me elliemcgough.me;" in conf
    assert "proxy_pass http://127.0.0.1:8000;" in conf
    for header in ["Host $host", "X-Forwarded-For $proxy_add_x_forwarded_for", "X-Forwarded-Proto $scheme"]:
        assert f"proxy_set_header {header};" in conf


def test_deploy_script_syncs_then_migrates_as_owner_then_restarts_then_checks():
    script = read("deploy.sh")
    assert script.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    steps = ["UV_PYTHON=/usr/bin/python3", "UV_PYTHON_PREFERENCE=only-system", "uv sync --locked",
             "/etc/career-platform/migrate.env", "alembic upgrade head", "systemctl restart career-platform",
             "/health", "/about"]
    positions = [script.index(step) for step in steps]
    assert positions == sorted(positions)


def test_deploy_script_is_executable():
    assert os.access(DEPLOY / "deploy.sh", os.X_OK)


def test_deploy_script_defaults_to_main():
    # After cutover the server runs main; an explicit ref (e.g. a known-good commit) still overrides it.
    assert 'ref="${1:-origin/main}"' in read("deploy.sh").splitlines()
