# Railway and PostgreSQL Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. As each section finishes, tick its boxes and add an `> **Executed YYYY-MM-DD: …**` note under it, the same way the earlier plans do.

**Goal:** Serve elliemcgough.me from the existing Railway project, with the site's data moved from the VM's SQLite file into the project's PostgreSQL service.

**Architecture:** The code stays the same FastAPI + SQLAlchemy app. Two small code changes let it run on Railway: Railway's `postgresql://` URL is rewritten to use the psycopg 3 driver, and a `railway.json` tells Railway how to build it, run the Alembic migrations before each deploy, start uvicorn on `$PORT`, and health-check `/health`. Railway deploys from GitHub `main`. The rows are copied once from a snapshot of the VM's SQLite file into Postgres by a tested script (`app/copy_data.py`). Then the Cloudflare DNS records for `elliemcgough.me` and `www` move from the VM to Railway. The VM is left running, unchanged, as the rollback.

**Tech Stack:** Railway (Railpack builder, managed PostgreSQL, Railway CLI), Python 3.12, uv, FastAPI, uvicorn, SQLAlchemy 2.1, Alembic, psycopg 3 (`psycopg[binary]`), Cloudflare DNS.

**Spec:** The request in chat on 2026-10-08: "Inspect my app and plan its move to Railway and PostgreSQL. The Railway project already exists with Postgres and a web service." It builds on `docs/superpowers/plans/2026-10-01-operate-the-vm.md`, which describes what runs on the VM today.

## What's there today (found 2026-10-08, read-only)

| Item | Value |
| --- | --- |
| Live site | `https://elliemcgough.me` and `www`, both A records to the VM, served by nginx + certbot on the VM |
| DNS | Cloudflare (`harley.ns.cloudflare.com`, `ulla.ns.cloudflare.com`). Cloudflare can flatten a CNAME at the apex, so the bare domain can point at Railway |
| VM code | `~/career-platform` at `59ab0fc`, clean working tree. systemd unit `career-platform`, 2 uvicorn workers on `127.0.0.1:8000` |
| VM data | `data/career_platform.db`, Alembic revision `0002_project_category`. Rows: profiles 1, experiences 2, education 2, skills 12, tags 13, projects 13, project_tags 27. Every value fits its `VARCHAR(n)` limit, which Postgres enforces and SQLite does not. Dates are stored as `YYYY-MM-DD` text |
| DB access | `app/config.py` reads `DATABASE_URL` (default `sqlite:///./career_platform.db`). `app/db.py` builds one engine. `alembic/env.py` migrates the same URL |
| Driver | None for Postgres. A plain `postgresql://` URL makes SQLAlchemy load psycopg2, which isn't installed, so the app would crash at import |
| Deps | `pyproject.toml` + `uv.lock` (what the VM uses) and a parallel unpinned `requirements.txt` |
| Proxy | `templates/base.html` builds the `og:image` URL from `request.base_url`. Behind Railway's proxy it reads `http://` unless uvicorn trusts the forwarded headers |
| Fallback | `load_public_profile` catches every DB error and shows `data/public_profile_snapshot.json`, marked by the HTML comment `Showing the latest saved profile snapshot.`. `/health` doesn't touch the DB. So a broken DB connection still returns 200 everywhere |
| SQL scripts | `scripts/*.sql` use SQLite-only syntax (`PRAGMA`, `INSERT OR IGNORE`). They were one-off content edits and are not run by this plan |
| Railway CLI | Not installed on the laptop. `psql` is not installed either; this plan doesn't need it |

## Global Constraints

- Railway project: already exists, with a PostgreSQL service and a web service. Their exact names are looked up in Section 4 Step 2 and written down as `<PG_SERVICE>` and `<WEB_SERVICE>`. The web service's generated domain is `<RAILWAY_DOMAIN>` (`*.up.railway.app`).
- Repo: `https://github.com/emcgough4/career-platform`, public. **No database URL, password or host may be committed or pasted into this plan.** Commands read them from Railway variables at run time.
- The web service gets its database through a Railway reference variable, `DATABASE_URL=${{<PG_SERVICE>.DATABASE_URL}}`, so it uses the private network and never a hard-coded password.
- Python 3.12 (from `.python-version`). Dependencies come from `uv.lock`.
- Postgres schema is created only by `alembic upgrade head`, never by `create_all`, so `alembic_version` stays correct.
- Local tests keep using SQLite. No test may need a running Postgres.
- **Content freeze:** no content edits on the VM from Section 6 Step 1 until the DNS cutover is done, or Railway will be missing them.
- The VM, its nginx, certbot and SQLite file are not changed or shut down by this plan.
- Code work happens on branch `railway-postgres`. Pushing and merging to `main` triggers a Railway deploy, so ask before pushing.
- SSH: `ssh -i ~/.ssh/isba4775_azure azureuser@172.214.156.151` (from `2026-10-01-operate-the-vm.md`).

## Review Focus

- **Explicit ids leave Postgres sequences at 1.** The copy inserts rows with their SQLite ids, so the next `INSERT` without an id would fail with a duplicate key. `copy_database` resets each `id` sequence to the table's max id. Section 6 Step 3 checks every sequence against `MAX(id)`.
- **Railway's `postgresql://` (or `postgres://`) URL picks psycopg2.** Task 1 rewrites both to `postgresql+psycopg://` and tests it at the settings level and the engine level.
- **A broken DB still looks healthy.** Because of the fallback, a 200 proves nothing. Section 5 Step 3 and Section 7 check for the real name `Eleanor McGough` and a fallback-marker count of 0, not just status codes.
- **Running the copy twice, or a copy failing halfway, duplicates or half-fills data.** `copy_database` refuses a target that already has rows or is on a different Alembic revision, and does the whole copy in one transaction. Task 3 tests both refusals.
- **Links built behind the proxy come out as `http://`.** Task 2 tests that the start command trusts forwarded headers. Section 7 Step 3 checks the live `og:image` starts with `https://`.

---

## 1. Code: Postgres driver and URL (Task 1)

### Task 1: Use psycopg 3 for Railway's Postgres URL

**Files:**
- Modify: `pyproject.toml`, `uv.lock` (via `uv add`), `requirements.txt`
- Modify: `app/config.py`
- Modify: `app/db.py:7-8`
- Test: `tests/test_config.py`, `tests/test_app_setup.py`

**Interfaces:**
- Produces: `app.config.normalize_database_url(url: str) -> str`. Turns `postgres://…` and `postgresql://…` into `postgresql+psycopg://…` and returns any other URL unchanged. `settings.database_url` is always the normalized URL. Task 3 imports this function.

- [ ] **Step 1: Create the branch**

```bash
git switch -c railway-postgres
```

- [ ] **Step 2: Write the failing tests**

Add to `tests/test_config.py` (keep the existing tests; add `import pytest` and the `app.config` import at the top):

```python
import pytest

from app.config import normalize_database_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("postgresql://u:p@db.example:5432/railway", "postgresql+psycopg://u:p@db.example:5432/railway"),
        ("postgres://u:p@db.example:5432/railway", "postgresql+psycopg://u:p@db.example:5432/railway"),
        ("postgresql+psycopg://u:p@db.example/railway", "postgresql+psycopg://u:p@db.example/railway"),
        ("sqlite:///./data/career_platform.db", "sqlite:///./data/career_platform.db"),
    ],
)
def test_normalize_database_url(raw, expected):
    assert normalize_database_url(raw) == expected


def test_database_url_rewrites_railway_postgres_url():
    url = "postgresql://u:p@db.example:5432/railway"
    assert read_database_url({"DATABASE_URL": url}) == "postgresql+psycopg://u:p@db.example:5432/railway"
```

Add to `tests/test_app_setup.py` (add `import os`, `import subprocess`, `import sys` and `from pathlib import Path` at the top if they aren't there):

```python
def test_postgres_engine_uses_psycopg_and_pre_ping():
    env = {**os.environ, "DATABASE_URL": "postgresql://u:p@localhost:5432/railway"}
    result = subprocess.run(
        [sys.executable, "-c", "from app.db import engine; print(engine.url.drivername, engine.pool._pre_ping)"],
        cwd=Path(__file__).resolve().parents[1], env=env, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "postgresql+psycopg True"
```

The engine is built without connecting, so no Postgres server is needed.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_config.py tests/test_app_setup.py -v`
Expected: collection error `ImportError: cannot import name 'normalize_database_url'`. With that import commented out, the engine test fails with `ModuleNotFoundError: No module named 'psycopg2'`.

- [ ] **Step 4: Add the driver**

```bash
uv add "psycopg[binary]"
echo 'psycopg[binary]' >> requirements.txt
```

`requirements.txt` gets the line too so the two dependency lists stay in step, whichever one Railpack reads.

- [ ] **Step 5: Write the implementation**

`app/config.py`:

```python
import os

from pydantic import BaseModel


def normalize_database_url(url: str) -> str:
    """Point Railway's postgres:// and postgresql:// URLs at the psycopg 3 driver."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Settings(BaseModel):
    app_name: str = "career-platform"
    database_url: str = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./career_platform.db"))
    # Show empty media slots where work is missing (local layout preview only; never set in production).
    preview_slots: bool = os.getenv("PREVIEW_SLOTS") == "1"


settings = Settings()
```

`app/db.py` lines 7-8 become:

```python
is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
# pool_pre_ping swaps out Postgres connections the server closed while they sat idle.
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=not is_sqlite, future=True)
```

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q`
Expected: all pass, including the existing `test_database_url_defaults_to_repo_root_sqlite` and `test_database_engine_uses_sqlite_thread_compatible_settings`.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock requirements.txt app/config.py app/db.py tests/test_config.py tests/test_app_setup.py
git commit -m "feat: connect to Railway Postgres through psycopg 3"
```

## 2. Code: Railway config (Task 2)

### Task 2: Tell Railway how to build, migrate, start and health-check

**Files:**
- Create: `railway.json`
- Test: `tests/test_railway_config.py`

**Interfaces:**
- Consumes: the `/health` route in `app/main.py`. `alembic/env.py` already migrates `settings.database_url`, which Task 1 normalizes.
- Produces: `railway.json`. Section 5 relies on its pre-deploy and health-check behavior.

- [ ] **Step 1: Write the failing test**

`tests/test_railway_config.py`:

```python
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
    assert CONFIG["deploy"]["healthcheckPath"] in {route.path for route in app.routes}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_railway_config.py -v`
Expected: collection error `FileNotFoundError: … railway.json`.

- [ ] **Step 3: Write `railway.json`**

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "preDeployCommand": ["alembic upgrade head"],
    "startCommand": "sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*'",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 60,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

- `sh -c` makes sure `$PORT` is expanded. Railway sets `PORT`, and the app must listen on it on `0.0.0.0`, not `127.0.0.1` as on the VM.
- One worker is enough on Railway; it restarts the process if it crashes. A failed migration stops the deploy before traffic moves, and the old deploy keeps serving.
- `--forwarded-allow-ips=*` is safe here because Railway's proxy is the only way in.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add railway.json tests/test_railway_config.py
git commit -m "feat: add Railway build, migrate, start and health-check config"
```

## 3. Code: SQLite → Postgres copy (Task 3)

### Task 3: A one-shot, all-or-nothing copy script

**Files:**
- Create: `app/copy_data.py`
- Test: `tests/test_copy_data.py`

**Interfaces:**
- Consumes: `app.config.normalize_database_url` (Task 1), `app.db.Base`, all tables registered by `app.models`.
- Produces: `app.copy_data.copy_database(source_url: str, target_url: str) -> dict[str, int]` (table name → rows copied), raising `ValueError` and copying nothing if the target already has rows or is on a different Alembic revision. Command line: `python -m app.copy_data <source_url> <target_url>`, printing one `table count` line per table. Section 6 runs it.

- [ ] **Step 1: Write the failing tests**

`tests/test_copy_data.py`:

```python
from datetime import date

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from app.copy_data import copy_database
from app.db import Base
from app.models import Experience, Profile, Project, Tag


def make_db(path, version="0002_project_category"):
    url = f"sqlite:///{path}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        conn.execute(text("INSERT INTO alembic_version VALUES (:v)"), {"v": version})
    engine.dispose()
    return url


def seed(url):
    engine = create_engine(url)
    with Session(engine) as session:
        profile = Profile(id=1, full_name="Eleanor McGough", headline="h", summary="s")
        session.add_all([
            profile,
            Experience(profile=profile, company_name="Co", role_title="Designer",
                       start_date=date(2024, 1, 1), is_current=True, description="d"),
            Project(profile=profile, title="Brand refresh", short_description="s",
                    long_description="l", featured=True, tags=[Tag(label="Brand")]),
        ])
        session.commit()
    engine.dispose()


def test_copies_every_row_with_types_intact(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db")
    seed(source)

    counts = copy_database(source, target)

    assert counts == {"profiles": 1, "tags": 1, "education": 0, "experiences": 1,
                      "projects": 1, "skills": 0, "project_tags": 1}
    with Session(create_engine(target)) as session:
        experience = session.scalars(select(Experience)).one()
        assert experience.is_current is True
        assert experience.start_date == date(2024, 1, 1)
        project = session.scalars(select(Project)).one()
        assert project.featured is True
        assert [tag.label for tag in project.tags] == ["Brand"]


def test_refuses_a_target_that_already_has_rows(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db")
    seed(source)
    seed(target)

    with pytest.raises(ValueError, match="already has rows"):
        copy_database(source, target)

    with create_engine(target).connect() as conn:
        assert conn.scalar(select(func.count()).select_from(Base.metadata.tables["projects"])) == 1


def test_refuses_a_target_on_another_migration(tmp_path):
    source = make_db(tmp_path / "source.db")
    target = make_db(tmp_path / "target.db", version="0001_core_schema")
    seed(source)

    with pytest.raises(ValueError, match="revision"):
        copy_database(source, target)
```

The expected `counts` keys follow `Base.metadata.sorted_tables` (parents before children). If the dict comparison fails only on key order, it doesn't matter: dicts compare without order.

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_copy_data.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'app.copy_data'`.

- [ ] **Step 3: Write the implementation**

`app/copy_data.py`:

```python
"""Copy every row from one database into another, empty one on the same migration.

Usage: python -m app.copy_data <source_url> <target_url>
"""

import sys

from sqlalchemy import create_engine, func, select, text

import app.models  # noqa: F401  registers every table on Base.metadata
from app.config import normalize_database_url
from app.db import Base

VERSION = text("SELECT version_num FROM alembic_version")


def copy_database(source_url: str, target_url: str) -> dict[str, int]:
    """Copy all tables in foreign-key order inside one target transaction."""
    source = create_engine(normalize_database_url(source_url))
    target = create_engine(normalize_database_url(target_url))
    tables = Base.metadata.sorted_tables
    counts: dict[str, int] = {}
    with source.connect() as src, target.begin() as dst:
        if src.scalar(VERSION) != dst.scalar(VERSION):
            raise ValueError("source and target are on a different Alembic revision; nothing was copied")
        for table in tables:
            if dst.scalar(select(func.count()).select_from(table)):
                raise ValueError(f"{table.name} in the target already has rows; nothing was copied")
        for table in tables:
            rows = [dict(row._mapping) for row in src.execute(select(table))]
            if rows:
                dst.execute(table.insert(), rows)
            counts[table.name] = len(rows)
        if dst.dialect.name == "postgresql":
            # Rows kept their ids, so move each id sequence past the highest one.
            for table in tables:
                if "id" in table.c:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"GREATEST(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table.name}"
                    ))
    source.dispose()
    target.dispose()
    return counts


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m app.copy_data <source_url> <target_url>")
    for name, count in copy_database(sys.argv[1], sys.argv[2]).items():
        print(name, count)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add app/copy_data.py tests/test_copy_data.py
git commit -m "feat: add one-shot SQLite to Postgres copy script"
```

## 4. Railway setup

Operator steps from the laptop. Steps that open a browser or prompt are run by the user with `! <command>`.

- [ ] **Step 1: Install and log in to the Railway CLI**
  - **Where:** laptop
  - **Run:** `brew install railway`, then the user runs `! railway login`
  - **Why:** The CLI sets variables, reads logs and runs the copy with Railway's credentials, so no database password is typed or saved locally.
  - **Check:** `railway whoami` prints the account.
  - **Undo:** `railway logout`; `brew uninstall railway`

- [ ] **Step 2: Link the repo to the project and record service names**
  - **Where:** laptop, repo root
  - **Run:** the user runs `! railway link` and picks the existing project and its `production` environment. Then `railway status --json | jq -r '.services.edges[].node.name'`
  - **Why:** Later commands need `<PG_SERVICE>` and `<WEB_SERVICE>`. Write them into the Executed note.
  - **Check:** Exactly two names print: the Postgres one and the web one.
  - **Undo:** `railway unlink`

- [ ] **Step 3: Give the web service the private database URL**
  - **Where:** laptop
  - **Run:** `railway variables --service <WEB_SERVICE> --set 'DATABASE_URL=${{<PG_SERVICE>.DATABASE_URL}}'` (single quotes so zsh leaves `${{…}}` alone)
  - **Why:** A reference variable follows the Postgres credentials if they rotate, and points at `*.railway.internal`, which is free and not exposed.
  - **Check:** `railway variables --service <WEB_SERVICE> --kv | grep '^DATABASE_URL=' | sed -E 's#.*@([^:/]+).*#\1#'` prints `postgres.railway.internal`. This prints only the host, never the password.
  - **Undo:** `railway variables --service <WEB_SERVICE> --set 'DATABASE_URL='`, or delete it in the dashboard.

- [ ] **Step 4: Connect the web service to GitHub and give it a domain**
  - **Where:** Railway dashboard → `<WEB_SERVICE>` → Settings → Source → Connect Repo `emcgough4/career-platform`, branch `main`. Then on the laptop: `railway domain --service <WEB_SERVICE>`
  - **Why:** Every push to `main` then deploys. The generated domain lets the site be checked before any DNS change.
  - **Check:** The dashboard shows the repo and `main`. The domain command prints `<RAILWAY_DOMAIN>`. Record it in the Executed note.
  - **Undo:** Disconnect the repo in the same settings panel; delete the domain under Settings → Networking.

## 5. Ship the code

- [ ] **Step 1: Push and merge (ask first)**
  - **Where:** laptop
  - **Run:** after the user says yes: `git push -u origin railway-postgres`, then `git switch main && git merge --ff-only railway-postgres && git push origin main`
  - **Why:** `main` is what Railway deploys. Nothing serves the real domain from Railway yet, so a bad deploy only affects `<RAILWAY_DOMAIN>`.
  - **Check:** `git log origin/main -1 --oneline` shows the Task 3 commit.
  - **Undo:** `git revert` the three commits on `main` and push. The VM is unaffected because it pulls only by hand.

- [ ] **Step 2: Read the build and deploy logs**
  - **Where:** laptop
  - **Run:** `railway logs --service <WEB_SERVICE> --build` and `railway logs --service <WEB_SERVICE> --deployment`
  - **Why:** It confirms the stack Railway chose and that the migrations ran.
  - **Check:** The build log shows Python 3.12 and a uv install that includes `psycopg`. The deploy log shows `Running upgrade  -> 0001_core_schema` and `Running upgrade 0001_core_schema -> 0002_project_category`, then uvicorn on `0.0.0.0:<port>`, and the health check passes. If the start fails with `uvicorn: not found`, change the start command to `.venv/bin/uvicorn …`, adjust the test in Task 2 to match, and redeploy.
  - **Undo:** none needed

- [ ] **Step 3: Check the empty site responds**
  - **Where:** laptop
  - **Run:** `curl -s https://<RAILWAY_DOMAIN>/health; curl -s https://<RAILWAY_DOMAIN>/about | grep -c 'Showing the latest saved profile snapshot'`
  - **Why:** The schema exists but has no rows yet, so `/about` should render with no name. A fallback marker here would mean the app can't reach Postgres.
  - **Check:** `{"status":"ok"}`, then `0`.
  - **Undo:** none needed

## 6. Copy the data

- [x] **Step 1: Start the content freeze and take a consistent snapshot on the VM**
  - **Where:** VM
  - **Run:** `cd ~/career-platform && sqlite3 data/career_platform.db ".backup data/railway-copy-2026-10-08.db" && sqlite3 data/railway-copy-2026-10-08.db "PRAGMA integrity_check;"`
  - **Why:** `.backup` gives a consistent copy even while the app reads. From here on, don't edit content on the VM.
  - **Check:** `ok`
  - **Undo:** `rm data/railway-copy-2026-10-08.db` on the VM

> **Executed 2026-10-08: Step 1 complete (run on its own, ahead of Sections 1-5).** `data/railway-copy-2026-10-08.db` was made with `.backup` (57344 bytes, mode 600). `PRAGMA integrity_check` returned `ok`. Row counts match the live DB: profiles 1, experiences 2, education 2, skills 12, tags 13, projects 13, project_tags 27. Revision `0002_project_category`, profile `Eleanor McGough`. The VM's `git status -s` is clean because the file is gitignored. **The content freeze starts now.** If content changes on the VM before Section 6 Step 3, take a new backup.

- [ ] **Step 2: Bring the snapshot to the laptop and count rows**
  - **Where:** laptop, repo root
  - **Run:**
    ```bash
    scp -i ~/.ssh/isba4775_azure azureuser@172.214.156.151:career-platform/data/railway-copy-2026-10-08.db data/
    git check-ignore data/railway-copy-2026-10-08.db
    uv run python -c "import sqlite3; c = sqlite3.connect('data/railway-copy-2026-10-08.db'); print({t: c.execute(f'select count(*) from {t}').fetchone()[0] for t in ['profiles','experiences','education','skills','tags','projects','project_tags']}, c.execute('select version_num from alembic_version').fetchone())"
    ```
  - **Why:** `git check-ignore` proves the personal data can't be committed (`data/*.db`). The counts are the target for Step 3.
  - **Check:** `check-ignore` prints the path. Counts are profiles 1, experiences 2, education 2, skills 12, tags 13, projects 13, project_tags 27 and the version is `0002_project_category`. Other numbers mean content changed since 2026-10-08; use the new numbers from here on.
  - **Undo:** `rm data/railway-copy-2026-10-08.db`

- [ ] **Step 3: Copy into Railway Postgres**
  - **Where:** laptop, repo root
  - **Run:**
    ```bash
    railway run --service <PG_SERVICE> -- sh -c 'uv run python -m app.copy_data sqlite:///./data/railway-copy-2026-10-08.db "$DATABASE_PUBLIC_URL"'
    ```
    Then check the sequences:
    ```bash
    railway run --service <PG_SERVICE> -- sh -c 'uv run python -c "
    import os
    from sqlalchemy import create_engine, text
    from app.config import normalize_database_url
    with create_engine(normalize_database_url(os.environ[\"DATABASE_PUBLIC_URL\"])).connect() as c:
        for t in [\"profiles\",\"experiences\",\"education\",\"skills\",\"tags\",\"projects\"]:
            print(t, c.scalar(text(f\"SELECT MAX(id) FROM {t}\")), c.scalar(text(f\"SELECT last_value FROM {t}_id_seq\")))
    "'
    ```
  - **Why:** `railway run` puts the Postgres variables into that one command's environment, so the password is never typed or saved. The laptop is outside Railway's private network, so it uses `DATABASE_PUBLIC_URL`.
  - **Check:** The copy prints the same counts as Step 2. In the sequence check, the two numbers on every line are equal. If the copy prints `already has rows`, nothing was written; find out why the target isn't empty before going further.
  - **Undo:** In the dashboard, Postgres → Data, truncate the seven tables (or run `TRUNCATE profiles, experiences, education, skills, tags, projects, project_tags RESTART IDENTITY CASCADE`). Then re-run.

## 7. Verify Railway serves the same site

- [ ] **Step 1: Pages match the VM byte for byte**
  - **Where:** laptop
  - **Run:**
    ```bash
    for p in /about /resume /portfolio /contact $(curl -s https://elliemcgough.me/portfolio | grep -oE 'href="/portfolio/[^"]+"' | cut -d'"' -f2 | sort -u); do
      diff <(curl -s "https://elliemcgough.me$p" | sed 's#https://elliemcgough.me#HOST#g') \
           <(curl -s "https://<RAILWAY_DOMAIN>$p" | sed 's#https://<RAILWAY_DOMAIN>#HOST#g') > /dev/null && echo "same $p" || echo "DIFF $p"
    done
    ```
  - **Why:** The only code change is in database setup, so the HTML should match the VM's exactly. This covers every project page.
  - **Check:** Every line says `same`. For a `DIFF`, re-run that path without `> /dev/null` and fix the cause before cutover.
  - **Undo:** none needed

- [ ] **Step 2: No fallback, real data**
  - **Where:** laptop
  - **Run:** `for p in /about /resume /portfolio; do curl -s https://<RAILWAY_DOMAIN>$p | grep -c 'Showing the latest saved profile snapshot'; done; curl -s https://<RAILWAY_DOMAIN>/about | grep -c 'Eleanor McGough'`
  - **Check:** `0` three times, then a number above 0.
  - **Undo:** none needed

- [ ] **Step 3: HTTPS links behind the proxy, and the 404 page**
  - **Where:** laptop
  - **Run:** `curl -s https://<RAILWAY_DOMAIN>/about | grep -o 'og:image" content="[^"]*'; curl -s -o /dev/null -w '%{http_code}\n' -H 'Accept: text/html' https://<RAILWAY_DOMAIN>/nope`
  - **Check:** The `og:image` URL starts with `https://` (if there is no `og:image`, the profile has no photo, which is fine). The 404 check prints `404`.
  - **Undo:** none needed

## 8. Cut the domain over to Railway

Gate: Section 7 all passed. This changes what the public sees; ask the user before Step 2.

- [ ] **Step 1: Add both hostnames to the web service**
  - **Where:** laptop
  - **Run:** `railway domain elliemcgough.me --service <WEB_SERVICE>` and `railway domain www.elliemcgough.me --service <WEB_SERVICE>`
  - **Why:** Railway prints the CNAME target (and a `_railway-verify` TXT record if it asks for one) for each name.
  - **Check:** Both commands print a target. Record them in the Executed note.
  - **Undo:** Remove the custom domains under Settings → Networking.

- [ ] **Step 2: Point Cloudflare DNS at Railway**
  - **Where:** Cloudflare dashboard → elliemcgough.me → DNS (done by the user)
  - **Run:** Replace the `elliemcgough.me` A record (`172.214.156.151`) with a CNAME to its Railway target, and the same for `www`. Set both to **DNS only** (grey cloud) so Railway can issue its own certificate. Add any TXT records Railway gave.
  - **Why:** Cloudflare flattens the apex CNAME, so the bare domain can follow Railway's address.
  - **Check:** `dig +short elliemcgough.me` and `dig +short www.elliemcgough.me` no longer print `172.214.156.151`. The dashboard shows both custom domains as active with a certificate (can take a few minutes).
  - **Undo:** Put back the two A records to `172.214.156.151`. The VM is still serving, so the site returns as soon as DNS updates.

- [ ] **Step 3: Check the real domain is on Railway**
  - **Where:** laptop
  - **Run:** `curl -sI https://elliemcgough.me/about | grep -i '^server'; curl -sI https://www.elliemcgough.me/about | grep -i '^server'; curl -s https://elliemcgough.me/about | grep -c 'Showing the latest saved profile snapshot'`
  - **Check:** Both `server` headers say `railway-edge` (the VM's say `nginx`), and the fallback count is `0`. The content freeze ends here.
  - **Undo:** Section 8 Step 2's undo.

## 9. After cutover (not done by this plan)

- Keep the VM running unchanged for at least a week as the rollback. Shutting it down, removing its NSG rules and renewing or dropping certbot are a separate plan.
- `docs/how-this-site-is-secured.md` describes nginx, certbot and the NSG on the VM. Once cutover holds, it needs rewriting for Railway.
- Future content edits go to Postgres. `scripts/*.sql` are SQLite-only (`PRAGMA`, `INSERT OR IGNORE`) and need Postgres versions (`ON CONFLICT DO NOTHING`, no `PRAGMA`) before they're used again.
- Delete `data/railway-copy-2026-10-08.db` from the laptop and VM once the VM is retired.
