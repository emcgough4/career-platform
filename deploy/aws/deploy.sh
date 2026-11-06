#!/usr/bin/env bash
set -euo pipefail
# Deploy a commit on the EC2 server. Run as ubuntu: deploy/aws/deploy.sh [git-ref]

ref="${1:-origin/aws-ec2-rds-migration}"
cd /opt/career-platform
git fetch origin
git checkout --detach "$ref"

# Ubuntu's own Python, not .python-version's 3.12 (kept for Railway) or a uv download the app user can't read.
UV_PYTHON=/usr/bin/python3 UV_PYTHON_PREFERENCE=only-system uv sync --locked

# Migrations run as the owner role; the app itself only gets the read-only role in app.env.
(
  set -a
  . /etc/career-platform/migrate.env
  set +a
  .venv/bin/alembic upgrade head
)

sudo systemctl restart career-platform

for _ in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS http://127.0.0.1:8000/health >/dev/null

status=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/about)
if [ "$status" != "200" ]; then
  echo "deploy failed: /about returned $status (503 means the database is unreachable)" >&2
  exit 1
fi
echo "deployed $(git rev-parse --short HEAD): /health ok, /about 200"
