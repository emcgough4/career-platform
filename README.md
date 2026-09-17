# Career Platform

## Codespace setup

```bash
python -m pip install -r requirements.txt
alembic upgrade head
sqlite3 career_platform.db < scripts/seed_profile.sql
uvicorn app.main:app --reload
```

Open `/about`, `/resume`, `/portfolio`, and `/contact`. Update content with
SQL scripts or direct SQLite statements. If SQLite is unavailable, public
pages use `data/public_profile_snapshot.json`.