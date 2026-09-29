# Azure VM Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the career-platform FastAPI site on the Azure VM `vm-career-platform`, serving the same SQLite data as the laptop.

**Architecture:** The code comes from GitHub via `git clone`. Python dependencies are installed with `uv sync --locked` from a committed `uv.lock`. Per-machine settings live in a `.env` copied from `.env.example`. The SQLite file is copied from the laptop with `scp` because it is never committed. uvicorn runs in the background on the VM, bound to `127.0.0.1:8000`. It is checked from inside the VM (or through an SSH tunnel), so no web port is opened to the internet.

**Tech Stack:** Azure VM (Ubuntu Server 24.04 LTS, `Standard_B2ats_v2`, North Central US), OpenSSH, apt, git, sqlite3, uv, Python 3.12, FastAPI, uvicorn, SQLAlchemy, SQLite.

**Spec:** The migration plan given in chat on 2026-09-24. Its eight categories, in order, are the sections below. It builds on `docs/superpowers/specs/2026-09-15-personal-resume-portfolio-design.md`, which names Azure VM as the production target.

## Global Constraints

- VM: `vm-career-platform` in resource group `rg-career-platform`, region `northcentralus`.
- **VM public IP: `<VM_PUBLIC_IP>`.** Look it up with `az vm show -d -g rg-career-platform -n vm-career-platform --query publicIps -o tsv`. `<LAPTOP_IP>` is the *laptop's* public IP (`curl -4 -s https://api.ipify.org`); it is used only as the allowed source in the SSH firewall rule. Both are placeholders, so the real addresses aren't published in this public repo.
- SSH user `azureuser`, key `~/.ssh/isba4775_azure`. Every SSH and scp command uses `-i ~/.ssh/isba4775_azure azureuser@<VM_PUBLIC_IP>`.
- Repo: `https://github.com/emcgough4/career-platform`, branch `main` (public, so it clones without credentials).
- App directory on the VM: `/home/azureuser/career-platform`. Every VM command below runs from there unless it says otherwise.
- Python 3.12, which is Ubuntu 24.04's system Python and matches the original build plan.
- The SQLite database must never be committed. The repo is public and the file holds personal profile data.
- No inbound port other than 22 is opened, and 22 is opened only to the laptop's IP.
- Nothing in this plan runs until the plan has been reviewed. (Reviewed and approved 2026-09-29; executing inline, one section at a time.)

## Review Focus

- **Empty database looks like success.** `data/career_platform.db` on the laptop currently has 0 rows in `profiles` and `projects`. The site will still answer 200 on the VM, but it will show the fallback snapshot ("Your Name" plus the "Showing the latest saved profile snapshot." banner). Data Step 1 stops the migration if the laptop DB is empty. Verify Step 3 fails if the banner appears.
- **Wrong working directory silently creates a new, empty DB.** `sqlite:///./…` is relative to the directory uvicorn starts in, and SQLite creates a missing file instead of failing. Processes Step 1 always `cd`s to the repo root. Verify Step 4 checks that no stray `career_platform.db` appeared.
- **uvicorn dies when the SSH session closes.** Processes Step 1 starts it with `setsid -f` and records the listening PID. Verify Step 5 reconnects in a fresh session and checks it is still up.
- **Laptop IP changes (new Wi-Fi or ISP reassignment) make SSH time out.** Server Step 1's check doubles as the diagnosis, and its undo/update command is given.
- **Accidentally committing the DB to the public repo.** Data Step 2 adds a `.gitignore` rule before any `git add`, and every commit in this plan names explicit paths.

---

## 1. Server

Azure VM, already created, reached over SSH.

- [x] **Step 1: Allow SSH from the laptop only**
  - **Where:** laptop (or portal: VM → Networking → Add inbound port rule, with the same values)
  - **Run:**
    ```bash
    az network nsg rule create -g rg-career-platform --nsg-name vm-career-platformNSG \
      -n AllowSSHFromLaptop --priority 1000 --direction Inbound --access Allow \
      --protocol Tcp --source-address-prefixes <LAPTOP_IP>/32 --destination-port-ranges 22
    ```
  - **Why:** The VM was created with no public inbound ports, so SSH is blocked. Opening port 22 only to the laptop's IP keeps the rest of the internet out.
  - **Check:** `az network nsg rule show -g rg-career-platform --nsg-name vm-career-platformNSG -n AllowSSHFromLaptop --query "{src:sourceAddressPrefix,port:destinationPortRange,access:access}" -o json` shows `<LAPTOP_IP>/32`, `22`, `Allow`.
  - **Undo:** `az network nsg rule delete -g rg-career-platform --nsg-name vm-career-platformNSG -n AllowSSHFromLaptop`. If the laptop IP changes later, re-run the create command with `--source-address-prefixes <new-ip>/32` (from `curl -4 -s https://api.ipify.org`).

- [x] **Step 2: First SSH login**
  - **Where:** laptop
  - **Run:**
    ```bash
    ssh -i ~/.ssh/isba4775_azure -o StrictHostKeyChecking=accept-new azureuser@<VM_PUBLIC_IP> \
      'hostname; lsb_release -ds; uname -m; free -h | head -2'
    ```
  - **Why:** This confirms the key, user, IP and firewall rule all work, and records the VM's host key in `~/.ssh/known_hosts`.
  - **Check:** Output shows `vm-career-platform`, `Ubuntu 24.04… LTS`, `x86_64`, and about 1 GiB of total memory. A timeout means the firewall rule or IP is wrong. `Permission denied (publickey)` means the key or user is wrong.
  - **Undo:** `ssh-keygen -R <VM_PUBLIC_IP>` removes the saved host key.

> **Executed 2026-09-29: complete.**
> - Step 1: Laptop IP re-checked and unchanged since 2026-09-24. Rule `AllowSSHFromLaptop` created; the check returned `<LAPTOP_IP>/32`, port `22`, `Allow`.
> - Step 2: SSH succeeded and the host key was saved. Output: `vm-career-platform`, `Ubuntu 24.04.4 LTS`, `x86_64`, 892 MiB total memory. That is below "about 1 GiB" because the kernel reserves some memory on a 1 GiB size; accepted.

## 2. Packages

apt-get: git, sqlite3.

- [x] **Step 1: Record what is already installed**
  - **Where:** VM
  - **Run:** `dpkg-query -W -f='${Package} ${Status}\n' git sqlite3 2>&1 | tee ~/preinstalled-packages.txt`
  - **Why:** Ubuntu cloud images usually ship with git. Recording this first lets the undo remove only what this plan added.
  - **Check:** The file exists and lists each package as `install ok installed` or "no packages found".
  - **Undo:** `rm ~/preinstalled-packages.txt`

- [x] **Step 2: Install git and sqlite3**
  - **Where:** VM
  - **Run:** `sudo apt-get update && sudo apt-get install -y git sqlite3`
  - **Why:** git clones the code. The sqlite3 CLI checks the copied database's integrity and row counts.
  - **Check:** `git --version && sqlite3 --version` both print versions.
  - **Undo:** `sudo apt-get remove -y <package>` for each package that `~/preinstalled-packages.txt` shows was *not* already installed. Never remove a package that was preinstalled.

> **Executed 2026-09-29: complete.**
> - Step 1: `~/preinstalled-packages.txt` shows `git install ok installed` and `no packages found matching sqlite3`. **Undo therefore removes only `sqlite3`; git came with the image.**
> - Step 2: Ran non-interactively (`DEBIAN_FRONTEND=noninteractive`, quiet, with output logged to `/tmp/apt-update.log` and `/tmp/apt-install.log` on the VM). Both commands exited 0. The check returned `git version 2.43.0` and `sqlite3 3.45.1`.

## 3. Code

git clone from GitHub.

- [x] **Step 1: Confirm the laptop and GitHub match**
  - **Where:** laptop, in `~/Desktop/career-platform`
  - **Run:** `git fetch origin && git status -sb`
  - **Why:** The VM gets whatever is on GitHub, not what is on the laptop.
  - **Check:** The first line is `## main...origin/main` with no `[ahead N]`. The only untracked file is `data/career_platform.db`.
  - **Undo:** Read-only; nothing to undo.

- [x] **Step 2: Clone on the VM**
  - **Where:** VM, in `~`
  - **Run:** `git clone https://github.com/emcgough4/career-platform.git ~/career-platform`
  - **Why:** It puts the code on the VM at a known path.
  - **Check:** `git -C ~/career-platform log --oneline -1` prints the same commit hash as `git log --oneline -1` on the laptop.
  - **Undo:** `rm -rf ~/career-platform`

> **Executed 2026-09-29: complete.**
> - Step 1: `## main...origin/main` with nothing ahead, at `b794545`. The untracked files were `data/career_platform.db` (expected) and this plan file, which isn't committed yet and isn't needed on the VM.
> - Step 2: Added a guard so the clone refuses to run if `~/career-platform` already exists. It cloned, and the VM is at `b794545`, matching the laptop.

## 4. Python

uv, then uv sync from the lock file.

> The repo currently has only `requirements.txt`, with no `pyproject.toml` or `uv.lock`, so `uv sync` has nothing to sync from. Steps 1–3 create and commit those on the laptop first.

- [x] **Step 1: Install uv on the laptop**
  - **Where:** laptop
  - **Run:** `brew install uv`
  - **Why:** The lock file is generated where the code is edited and committed.
  - **Check:** `uv --version` prints a version.
  - **Undo:** `brew uninstall uv`

- [x] **Step 2: Create `pyproject.toml`, `.python-version` and `uv.lock` from `requirements.txt`**
  - **Where:** laptop, in `~/Desktop/career-platform`
  - **Run:**
    ```bash
    uv init --bare --name career-platform --python 3.12
    uv python pin 3.12
    uv add -r requirements.txt
    uv add httpx2 && echo httpx2 >> requirements.txt   # added during execution; see note below
    printf '\n[tool.pytest.ini_options]\npythonpath = ["."]\n' >> pyproject.toml   # added during execution
    ```
  - **Why:** This turns the unpinned `requirements.txt` into exact, locked versions, so the VM installs exactly what the laptop tested. Pinning 3.12 matches Ubuntu 24.04's system Python. `requirements.txt` stays in place so the README's Codespace steps still work.
  - **Check:** `pyproject.toml` has `requires-python = ">=3.12"` and the seven dependencies. `.python-version` contains `3.12`. `uv.lock` exists. `uv run pytest -q` passes.
  - **Undo:** `rm -rf pyproject.toml .python-version uv.lock .venv`

- [x] **Step 3: Commit and push the Python project files**
  - **Where:** laptop
  - **Run:**
    ```bash
    git add pyproject.toml .python-version uv.lock requirements.txt
    git commit -m "build: add uv project and lock file for VM deploy"
    git push origin main
    ```
  - **Why:** The VM gets the lock file through GitHub. The explicit paths keep the database out of the commit.
  - **Check:** `git status -sb` shows `## main...origin/main` with no `ahead`. `git show --stat HEAD` lists exactly those four files.
  - **Undo:** `git revert HEAD && git push origin main`

- [x] **Step 4: Install uv on the VM**
  - **Where:** VM
  - **Run:** `curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.local/bin/env`
  - **Why:** It installs uv for `azureuser` only, with no sudo, into `~/.local/bin`.
  - **Check:** In a *new* SSH session, `uv --version` prints a version, which proves PATH persists.
  - **Undo:** `rm -f ~/.local/bin/uv ~/.local/bin/uvx ~/.local/bin/env && rm -rf ~/.local/share/uv ~/.cache/uv`, then remove the line the installer added to `~/.bashrc` and `~/.profile`.

- [x] **Step 5: Pull and sync**
  - **Where:** VM, in `~/career-platform`
  - **Run:** `git pull --ff-only && uv sync --locked`
  - **Why:** `--locked` fails instead of silently re-resolving if `uv.lock` doesn't match `pyproject.toml`, so the VM gets exactly the laptop's versions.
  - **Check:** `uv run python -c "import sys, fastapi, sqlalchemy, uvicorn; print(sys.version)"` prints `3.12.x`. `uv run pytest -q` passes. **Then delete the empty DB the tests leave behind:** `find . -maxdepth 1 -name career_platform.db -size 0 -delete -print`, and `git status -s` must be clean.
  - **Undo:** `rm -rf ~/career-platform/.venv`

> **Executed 2026-09-29: complete (commit `89e3729`, pushed to `main` with the user's OK).**
> - Step 1: `brew install uv` gave `uv 0.12.19`.
> - Step 2: The generated files matched the plan, and uv downloaded CPython 3.12.14 for the laptop. The first `uv run pytest -q` failed to start (exit 4), which led to two changes:
>   1. `starlette.testclient` needs `httpx2` (or `httpx`), which was never declared; the Codespace probably had one installed by chance. The user chose `httpx2` and ran `uv add httpx2 && echo httpx2 >> requirements.txt` themselves, because the permission check blocked Claude from adding a dependency.
>   2. `ModuleNotFoundError: No module named 'app'`: plain `pytest` doesn't put the repo root on the import path (`python -m pytest` does, and that gave 15 passed). Added `[tool.pytest.ini_options] pythonpath = ["."]` to `pyproject.toml`.
>
>   After both changes: 15 passed, and `uv lock --check` is OK.
> - Step 3: The commit also includes `requirements.txt` (for `httpx2`), so it has 4 files. Pushed `b794545..89e3729`.
> - Step 4: The VM has uv 0.12.21 at `~/.local/bin/uv`, visible in a new login shell. The small version gap from the laptop doesn't matter because the lock file format is the same.
> - Step 5: The VM pulled `89e3729`. `uv sync --locked` exited 0. Python is `3.12.3` (Ubuntu's system Python). 15 passed.
> - **Found:** the test suite hits real routes with the default `sqlite:///./career_platform.db`, so every test run creates an **empty `career_platform.db` at the repo root** (on both the laptop and the VM). It's not gitignored, and it's the same stray file Verify Step 4 looks for. Both 0-byte copies were deleted; the VM's `git status` is clean. Changes made: Step 5 now deletes the file after tests, and Data Step 2 also ignores `/career_platform.db`. Test isolation, meaning tests that don't touch a real DB path, is left for the final review.

## 5. Config

Copy .env from .env.example.

> `.env.example` does not exist, and `app/config.py` hardcodes `database_url` instead of reading the environment. Steps 1–5 make the setting configurable (test first), then add the example file.

- [x] **Step 1: Write the failing test**
  - **Where:** laptop
  - **Create** `tests/test_config.py`:
    ```python
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
    ```
  - **Why:** It pins the new behavior, and also pins the old default so the Codespace workflow doesn't change.
  - **Check:** `uv run pytest tests/test_config.py -v`: `test_database_url_reads_environment` FAILS (it prints the default), and the default test passes.
  - **Undo:** `rm tests/test_config.py`

- [x] **Step 2: Read `DATABASE_URL` from the environment**
  - **Where:** laptop
  - **Modify** `app/config.py` to:
    ```python
    import os

    from pydantic import BaseModel


    class Settings(BaseModel):
        app_name: str = "career-platform"
        database_url: str = os.getenv("DATABASE_URL", "sqlite:///./career_platform.db")


    settings = Settings()
    ```
  - **Why:** Without this, a `.env` file would have no effect.
  - **Check:** `uv run pytest -q` passes, including both new tests.
  - **Undo:** `git checkout app/config.py`

- [x] **Step 3: Create `.env.example`**
  - **Where:** laptop
  - **Create** `.env.example`:
    ```
    # Copy to .env and adjust per machine. Loaded by: uvicorn --env-file .env
    # Relative sqlite paths resolve from the directory uvicorn is started in (the repo root).
    DATABASE_URL=sqlite:///./data/career_platform.db
    ```
  - **Why:** It documents the one setting the app reads and points it at `data/`, where the DB lives on the laptop and will live on the VM. `.env` itself is already gitignored.
  - **Check:** `git check-ignore .env` prints `.env`. `git check-ignore .env.example` prints nothing.
  - **Undo:** `rm .env.example`

- [x] **Step 4: Commit and push**
  - **Where:** laptop
  - **Run:**
    ```bash
    git add app/config.py tests/test_config.py .env.example
    git commit -m "feat: read DATABASE_URL from environment; add .env.example"
    git push origin main
    ```
  - **Why:** The VM gets config support through GitHub.
  - **Check:** `git show --stat HEAD` lists exactly those three files. `git status -sb` shows no `ahead`.
  - **Undo:** `git revert HEAD && git push origin main`

- [x] **Step 5: Create `.env` on the VM**
  - **Where:** VM, in `~/career-platform`
  - **Run:** `git pull --ff-only && cp -n .env.example .env && chmod 600 .env`
  - **Why:** `-n` never overwrites an existing `.env`, and `600` keeps it private to `azureuser`.
  - **Check:** `cat .env` shows `DATABASE_URL=sqlite:///./data/career_platform.db`. `set -a; . ./.env; set +a; uv run python -c "from app.config import settings; print(settings.database_url)"` prints the same URL.
  - **Undo:** `rm ~/career-platform/.env`

> **Executed 2026-09-29: complete (commit `5c4f897`, pushed to `main`).**
> - Step 1: RED as expected: `test_database_url_reads_environment` FAILED (it got the default URL); `test_database_url_defaults_to_repo_root_sqlite` PASSED.
> - Step 2: GREEN: the full suite gives 17 passed. The test run left the empty root `career_platform.db` again, and the 0-byte file was deleted (see the note under Python).
> - Step 3: `git check-ignore .env` gives `.env`; `.env.example` is not ignored.
> - Step 4: The commit has exactly 3 files (`.env.example`, `app/config.py`, `tests/test_config.py`). Pushed `89e3729..5c4f897`.
> - Step 5: The VM pulled `5c4f897`. `.env` is created with mode `-rw-------`, and settings print `sqlite:///./data/career_platform.db`. `cp -n` printed a harmless coreutils portability warning; there was no existing `.env`. The VM's `git status` is clean.

## 6. Data

scp the SQLite .db file from the laptop.

- [x] **Step 1: Confirm the laptop DB actually has data (STOP if not)**
  - **Where:** laptop, in `~/Desktop/career-platform`
  - **Run:**
    ```bash
    sqlite3 data/career_platform.db "PRAGMA integrity_check; SELECT version_num FROM alembic_version; SELECT 'profiles', count(*) FROM profiles; SELECT 'projects', count(*) FROM projects;"
    ```
  - **Why:** As of 2026-09-24 this file has **0 profiles and 0 projects**. Copying it would give a site that answers but only shows the placeholder fallback snapshot.
  - **Check:** `ok`, `0001_core_schema`, and `profiles` ≥ 1. If `profiles` is 0, stop and decide first: load real content (for example, edit `scripts/seed_profile.sql` and run `sqlite3 data/career_platform.db < scripts/seed_profile.sql`), or confirm the DB is at a different path.
  - **Undo:** Read-only; nothing to undo.

- [x] **Step 2: Gitignore the database**
  - **Where:** laptop
  - **Run:**
    ```bash
    printf '\n# Local SQLite data (never commit; copied to servers with scp)\ndata/*.db\ndata/*.db-journal\ndata/*.db-wal\ndata/*.db-shm\n# empty DB created at repo root by test runs / default DATABASE_URL\n/career_platform.db\n' >> .gitignore
    git add .gitignore
    git commit -m "chore: ignore local SQLite databases in data/"
    git push origin main
    ```
  - **Why:** The repo is public, and `data/career_platform.db` currently shows as untracked (`??`), one `git add .` away from being published.
  - **Check:** `git check-ignore -v data/career_platform.db` names the new rule. `git status -s` no longer lists the DB.
  - **Undo:** `git revert HEAD && git push origin main`

- [x] **Step 3: Record the laptop checksum**
  - **Where:** laptop
  - **Run:** `shasum -a 256 data/career_platform.db`
  - **Why:** Step 5 compares it to the VM's copy.
  - **Check:** A 64-character hash is printed. Note it down.
  - **Undo:** Nothing to undo.

- [x] **Step 4: Copy the DB to the VM**
  - **Where:** laptop, in `~/Desktop/career-platform`
  - **Run:**
    ```bash
    ssh -i ~/.ssh/isba4775_azure azureuser@<VM_PUBLIC_IP> 'test ! -e ~/career-platform/data/career_platform.db' \
      && scp -i ~/.ssh/isba4775_azure data/career_platform.db azureuser@<VM_PUBLIC_IP>:career-platform/data/career_platform.db
    ```
  - **Why:** The DB isn't in git, so it has to be copied. The `test ! -e` guard refuses to overwrite a DB that is already on the VM. Nothing writes to the laptop DB during the copy, so a plain file copy is consistent.
  - **Check:** scp exits 0.
  - **Undo:** `rm ~/career-platform/data/career_platform.db` on the VM.

- [x] **Step 5: Verify the copy on the VM**
  - **Where:** VM, in `~/career-platform`
  - **Run:**
    ```bash
    chmod 600 data/career_platform.db
    sha256sum data/career_platform.db
    sqlite3 data/career_platform.db "PRAGMA integrity_check; SELECT version_num FROM alembic_version; SELECT count(*) FROM profiles; SELECT full_name FROM profiles ORDER BY id LIMIT 1;"
    ```
  - **Why:** It proves the file arrived intact, and it gets the exact `full_name` to look for in Verify.
  - **Check:** The hash matches Step 3. Integrity is `ok`, the version is `0001_core_schema`, and the counts match Step 1. Note the `full_name`.
  - **Undo:** Read-only; nothing to undo.

> **Executed 2026-09-29: complete, with placeholder content (the user chose option 2).**
> - Step 1: The first check failed: integrity `ok` and `0001_core_schema`, but **0 rows in every table**. No other copy of the DB was found under `~`. The user chose to migrate with the placeholder seed and replace it with real content later. The empty DB was backed up to `.superpowers/sdd/2026-09-24-azure-vm-migration/career_platform.db.pre-seed.bak`, then `sqlite3 -bail data/career_platform.db < scripts/seed_profile.sql` ran (exit 0). Re-check: `ok`, `0001_core_schema`, profiles 1 (`Your Name`), skills 3, **projects 0** (the seed script has none, so Portfolio will be empty), experiences 0, education 0.
> - Step 2: `.gitignore` rules include `/career_platform.db`, and `git check-ignore` confirmed both paths. Commit `61d5763`, pushed `5c4f897..61d5763`. This was done before the user's decision because it doesn't depend on the data.
> - Step 3: sha256 `43905dab91ba75f455b344399fdbbc09082102f8912df07abc0d6d45748daecd`.
> - Step 4: The no-overwrite guard passed and scp exited 0.
> - Step 5: The VM's sha256 matches, integrity is `ok`, the version is `0001_core_schema`, profiles 1, and `full_name` = **`Your Name`** (used in Verify Step 3). Mode is `-rw-------`. The VM's `git status` first showed the DB as untracked because the VM hadn't pulled `61d5763`; after `git pull --ff-only` it is ignored and the status is clean.
> - **Later:** to switch to real content, update the laptop DB (or `scripts/seed_profile.sql` plus `scripts/update_profile.sql`), then repeat Steps 3–5. Step 4's guard means you must first `mv` the VM copy aside (for example `data/career_platform.db.bak`) and stop uvicorn while replacing it.

## 7. Processes

Start uvicorn.

- [x] **Step 1: Start uvicorn in the background**
  - **Where:** VM
  - **Run** *(amended during execution; see the note below)*:
    ```bash
    cd ~/career-platform && setsid -f ~/.local/bin/uv run --locked uvicorn app.main:app \
      --host 127.0.0.1 --port 8000 --env-file .env \
      > ~/career-platform/uvicorn.log 2>&1 < /dev/null
    for i in $(seq 1 40); do P=$(ss -ltnpH "sport = :8000" | grep -o "pid=[0-9]*" | head -1 | cut -d= -f2); [ -n "$P" ] && break; sleep 0.5; done
    echo "$P" > ~/career-platform/uvicorn.pid
    ```
  - **Why:**
    - The `cd` matters because `static/`, `templates/` and the relative SQLite path all resolve from the working directory.
    - `setsid -f` puts uvicorn in its own session, so it survives SSH logout. Unlike `nohup … &`, the redirects apply to `setsid` itself, so no process keeps the SSH output open and the SSH command returns.
    - The PID file records the process that is actually **listening** (uvicorn), not the `uv` wrapper.
    - `--env-file` loads `DATABASE_URL`.
    - Binding to `127.0.0.1` keeps port 8000 off the internet.
  - **Check:** `tail -n 5 ~/career-platform/uvicorn.log` shows `Loading environment from '.env'`, `Application startup complete.` and `Uvicorn running on http://127.0.0.1:8000`. `ss -ltnp | grep 8000` shows `127.0.0.1:8000` with the same PID as `uvicorn.pid`.
  - **Undo:** `kill "$(cat ~/career-platform/uvicorn.pid)" && rm ~/career-platform/uvicorn.pid`. The `uv` wrapper exits with it. Confirm with `ss -ltn | grep :8000` printing nothing.

> **Executed 2026-09-29: complete (uvicorn PID 40501).**
> - First attempt, with the plan's original `nohup uv run … &` plus `echo $! > uvicorn.pid`: the server started fine, but **the SSH command never returned**, because the remote shell running the background job kept SSH's stdout/stderr pipes open. Also, **`uvicorn.pid` held that wrapper shell's PID (40008), not uvicorn's (40013)**, so the plan's undo would have missed the server.
> - Checked: after the hung SSH was closed, uvicorn kept running and `/health` returned `ok`. Killing uvicorn's own PID freed port 8000, the `uv` wrapper exited too, and no processes were left. That confirms the undo works when the PID file is correct.
> - A second try, `setsid nohup … &`, still hung for the same reason. The final form, `setsid -f … > log 2>&1 < /dev/null` with no `&` and the PID read from `ss`, **returned immediately (exit 0)**.
> - Checks in a new SSH session: the log shows `.env` loaded and startup complete. The listener is `127.0.0.1:8000` with pid 40501, matching `uvicorn.pid`. `/health` gives `{"status":"ok"}`. There is no root `career_platform.db`. `git status` is clean, because `*.log` and `*.pid` are already in `.gitignore`.

## 8. Verify

The site answers on the VM and shows your data.

- [x] **Step 1: Health endpoint**
  - **Where:** VM
  - **Run:** `curl -s http://127.0.0.1:8000/health`
  - **Why:** It checks that the app is up, separately from the data.
  - **Check:** `{"status":"ok"}`
  - **Undo:** Read-only.

- [x] **Step 2: Every public page returns 200**
  - **Where:** VM
  - **Run:** `for p in / /about /resume /portfolio /contact; do printf '%s ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8000$p"; done`
  - **Why:** It confirms routes, templates and static files all resolve on the VM.
  - **Check:** All five print `200`.
  - **Undo:** Read-only.

- [x] **Step 3: Pages show DB data, not the fallback**
  - **Where:** VM
  - **Run:**
    ```bash
    curl -s http://127.0.0.1:8000/about | grep -c "Showing the latest saved profile snapshot"
    curl -s http://127.0.0.1:8000/about | grep -F "<full_name from Data Step 5>"
    ```
  - **Why:** The fallback also returns 200, so status codes alone can't prove the DB is being read.
  - **Check:** The first command prints `0`. The second prints a line containing your name.
  - **Undo:** Read-only.

- [x] **Step 4: No stray database was created**
  - **Where:** VM
  - **Run:** `ls -la ~/career-platform/career_platform.db 2>&1; grep -iE "error|traceback" ~/career-platform/uvicorn.log`
  - **Why:** A wrong `DATABASE_URL` or working directory makes SQLite silently create a new, empty DB at the repo root. (Running `uv run pytest` also creates it; if tests were run on the VM after Python Step 5, delete the 0-byte file and restart uvicorn before this check.)
  - **Check:** `ls` reports `No such file or directory`, and `grep` prints nothing.
  - **Undo:** Read-only.

- [x] **Step 5: Survives SSH logout, and view it in the laptop browser**
  - **Where:** laptop
  - **Run:** `ssh -i ~/.ssh/isba4775_azure -N -L 8000:127.0.0.1:8000 azureuser@<VM_PUBLIC_IP>`, then open `http://localhost:8000/about` on the laptop. (Stop any local uvicorn on port 8000 first.)
  - **Why:** It is a fresh session, which proves `setsid -f` worked, and it lets you check the pages visually without opening port 8000 on the VM.
  - **Check:** The About, Resume, Portfolio and Contact pages show your data, with no fallback banner.
  - **Undo:** Ctrl+C closes the tunnel.

---

> **Executed 2026-09-29: complete.**
> - Step 1: `{"status":"ok"}`.
> - Step 2: `/`, `/about`, `/resume`, `/portfolio` and `/contact` all return `200`.
> - Step 3: On all four HTML pages the banner count is `0`, and "Your Name" appears (`<title>About · Your Name</title>`, `<h1>Your Name</h1>`). **Proof that the DB is being read:** `/resume` lists `Brand strategy`, `Marketing` and `Visual design`. Those skills exist only in the DB; `data/public_profile_snapshot.json` has `"skills": []`.
> - Step 4: There is no `~/career-platform/career_platform.db`, and `uvicorn.log` has no `error`/`traceback` lines (`grep` exit 1).
> - Step 5: Laptop port 8000 was free. The tunnel was opened in the background with `ssh -f -N -L 8000:127.0.0.1:8000 … -o ExitOnForwardFailure=yes` (pid 83067) instead of in the foreground. Through `http://localhost:8000`: `/health` and all four pages return `200` with banner `0`, `<h1>Your Name</h1>` is present, and the static CSS returns `200`. The server had been running across several separate SSH sessions since Processes Step 1, which proves it survives logout. **Left for the user:** the visual check in a browser. Close the tunnel afterwards with `kill 83067`.
> - **Known, by the user's choice (Data, option 2):** the content is the placeholder seed ("Your Name", 3 skills), and Portfolio shows no projects.

## Post-plan changes

> **2026-09-29: uvicorn rebound from `127.0.0.1` to `0.0.0.0:8000` at the user's request.** No Azure changes were made.
> - Ran: `kill "$(cat uvicorn.pid)"` (port freed), then the Processes Step 1 command with `--host 0.0.0.0`. New PID 40887, which matches `uvicorn.pid`.
> - `ss -ltnp` shows `0.0.0.0:8000` uvicorn, `0.0.0.0:22` / `[::]:22` sshd, and `127.0.0.53`/`127.0.0.54:53` systemd-resolved. `/health` returns `ok` on both `127.0.0.1` and the private IP `10.0.0.4`. The `.env` loaded and the DB is still read (skills render, no banner).
> - **The Global Constraint "No inbound port other than 22 is opened" still holds at the Azure network security group (NSG), but no longer at the VM itself.** `ufw` is inactive, so the only thing keeping 8000 off the internet is the NSG, which allows only 22 from the laptop's IP. If an NSG rule for 8000 is ever added, the site is directly public over plain HTTP.
> - The SSH tunnel in Verify Step 5 still works, because `0.0.0.0` includes `127.0.0.1`.
> - Undo: restart with `--host 127.0.0.1` (Processes Step 1 as written).

> **2026-09-29: `/` now redirects to `/about` (commit `0546382`, pushed to `main`).** The user reported that loading the site showed only "career-platform is running", which was the old plain-text root route.
> - TDD: added `test_root_route_redirects_to_about`, which asserts `307` and `location: /about`. It failed first (`200 == 307`), and after the change 18 passed. Removed the now-unused `settings` import from `app/main.py`.
> - VM: pulled `0546382` and restarted on `0.0.0.0:8000` (PID 41065, matching `uvicorn.pid`; `.env` loaded). `/` gives `307` to `/about`, and following it shows `<h1>Your Name</h1>`. It also works through the tunnel.
> - Undo: `git revert 0546382 && git push origin main`, then pull on the VM and restart.

## Full rollback (reverse order)

1. VM: `kill "$(cat ~/career-platform/uvicorn.pid)"` (the PID file holds uvicorn's listening PID, as set in Processes Step 1)
2. VM: `rm -rf ~/career-platform`
3. VM: remove uv (Python Step 4 undo), then remove packages this plan added (Packages Step 2 undo).
4. Laptop: `git revert` the three commits from Python Step 3, Config Step 4 and Data Step 2, then `git push origin main`.
5. Laptop: delete the `AllowSSHFromLaptop` firewall rule (Server Step 1 undo).
