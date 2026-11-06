import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_offline_migration_accepts_percent_encoded_password():
    # alembic/env.py hands the URL to configparser, where a bare % starts an interpolation.
    env = {**os.environ, "DATABASE_URL": "postgresql://u:p%40ss@db.example:5432/career_platform"}
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
                            cwd=REPO_ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "CREATE TABLE profiles" in result.stdout
