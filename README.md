# Career Platform

A FastAPI résumé and portfolio site (`/about`, `/resume`, `/portfolio`, `/projects/<id>`, `/contact`), served at https://elliemcgough.me.

## How it runs

The site runs on [Railway](https://railway.com), in the project `astonishing-vision`, environment `production`:

| Service | What it is |
| --- | --- |
| `career-platform` | The web app. Its `DATABASE_URL` is a reference to the Postgres service's private URL (`postgres.railway.internal`). |
| `Postgres` | The site's data. The schema comes from the Alembic migrations in `alembic/versions/`. |

Each deploy goes through these steps:

1. **Build.** Railpack installs Python 3.12 (from `.python-version`) and runs `pip install -r requirements.txt`. It starts the app with the command in `railpack.json`.
2. **Pre-deploy.** `railway.json` runs `alembic upgrade head`. If the migration fails, the new deploy stops and the previous one keeps serving.
3. **Start.** uvicorn listens on `0.0.0.0:$PORT` (Railway sets 8080) and trusts Railway's proxy headers, so the URLs the app builds use `https://`.
4. **Health check.** Railway checks `/health` before sending traffic to the new deploy. `/health` doesn't touch the database.

`railpack.json` and `railway.json` must have the same start command; `tests/test_railway_config.py` checks this.

DNS is on Cloudflare. `elliemcgough.me` is a CNAME to Railway, set to DNS only (grey cloud), and Railway issues the certificate. `www.elliemcgough.me` still points at the old Azure VM until it is moved.

## Deploy

Every push to `main` on GitHub deploys automatically. To deploy local changes without pushing, or to check on a deploy, use the [Railway CLI](https://docs.railway.com/guides/cli):

```bash
railway login
railway link          # project astonishing-vision, environment production
railway up --service career-platform --ci     # deploy the working tree without pushing
railway deployment list --service career-platform
railway logs --service career-platform
```

## Dependencies

`pyproject.toml` and `uv.lock` are the source of truth. Railway installs from `requirements.txt` with pip, so after any dependency change, regenerate that file from the lock:

```bash
uv add <package>
uv export --format requirements-txt --no-hashes --no-emit-project --locked -o requirements.txt
```

`tests/test_requirements.py` fails if any line in `requirements.txt` isn't pinned.

## Edit content

Content lives in the Railway Postgres database; there is no admin page. Pages read the database on every request, so changes show up without a redeploy.

```bash
railway connect Postgres     # opens psql (needs psql on PATH)
```

`railway run --service Postgres -- <command>` gives a single command the database URL in `$DATABASE_PUBLIC_URL`, so the password is never typed or saved.

The scripts in `scripts/*.sql` use SQLite syntax (`PRAGMA`, `INSERT OR IGNORE`). Convert them to Postgres syntax before running them against Railway.

If the database can't be reached, public pages fall back to `data/public_profile_snapshot.json`. The HTML then contains the comment `Showing the latest saved profile snapshot.`, so `/health` returning 200 does not by itself prove the data is live.

## Local development

Locally the app uses SQLite (`sqlite:///./career_platform.db` unless `DATABASE_URL` says otherwise):

```bash
uv sync
uv run alembic upgrade head
sqlite3 career_platform.db < scripts/seed_profile.sql
uv run uvicorn app.main:app --reload
uv run pytest
```

To run against Postgres instead, set `DATABASE_URL` to a `postgresql://` or `postgres://` URL. The app switches it to the psycopg 3 driver.

`python -m app.copy_data <source_url> <target_url>` copies every table from one database into an empty one on the same migration. It was used for the one-time move from the VM's SQLite file to Railway.
