import json
from pathlib import Path


FALLBACK_PATH = Path(__file__).resolve().parents[2] / "data" / "public_profile_snapshot.json"


def load_latest_snapshot() -> dict:
    if not FALLBACK_PATH.exists():
        return {"profile": {}, "experience": [], "education": [], "skills": [], "projects": []}
    return json.loads(FALLBACK_PATH.read_text(encoding="utf-8"))


def write_snapshot(snapshot: dict) -> None:
    FALLBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    FALLBACK_PATH.write_text(json.dumps(snapshot, indent=2, default=str) + "\n", encoding="utf-8")
