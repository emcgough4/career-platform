import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read_database_url(extra_env: dict[str, str]) -> str:
    env = {key: value for key, value in os.environ.items() if key != "DATABASE_URL"}
    env.update(extra_env)
    result = subprocess.run(
        [sys.executable, "-c", "from app.config import settings; print(settings.database_url)"],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def test_database_url_defaults_to_repo_root_sqlite():
    assert read_database_url({}) == "sqlite:///./career_platform.db"


def test_database_url_reads_environment():
    url = "sqlite:///./data/career_platform.db"
    assert read_database_url({"DATABASE_URL": url}) == url
