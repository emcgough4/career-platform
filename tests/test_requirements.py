from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


def test_requirements_are_pinned_to_the_lock_file():
    # Railway's builder installs with pip from requirements.txt, so it must match uv.lock exactly.
    lines = [line.split(";")[0].split("\\")[0].strip() for line in REQUIREMENTS.read_text().splitlines()]
    packages = [line for line in lines if line and not line.startswith(("#", "--"))]
    assert packages
    assert all("==" in package for package in packages), [p for p in packages if "==" not in p]
