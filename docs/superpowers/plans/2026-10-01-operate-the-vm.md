# Operate the VM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the career-platform site like a real website at `http://172.214.156.151` (no port number). It starts on boot, comes back after a crash, and is never exposed on port 8000 or run as root.

**Architecture:** **systemd** is Linux's built-in process manager. It runs uvicorn as `azureuser` on `127.0.0.1:8000` with 2 worker processes. **nginx** listens on port 80 and passes every request on to uvicorn. The Azure firewall lets port 80 in and keeps 8000 shut.

**Tech Stack:** Ubuntu 24.04, systemd, nginx (from apt), uvicorn 0.54.0, Python 3.12.3. The code, `.venv` and SQLite DB are already in `~/career-platform`.

**Spec:** The request in chat on 2026-10-01. This plan builds on `docs/superpowers/plans/2026-09-24-azure-vm-migration.md`, which put the code, Python environment and data on the VM.

## VM details (found 2026-10-01, read-only)

| | |
|---|---|
| Subscription | Azure for Students |
| VM | `vm-career-platform` in `rg-career-platform`, `northcentralus`, `Standard_B2ats_v2` (2 vCPUs, 887 MiB RAM) |
| OS | Ubuntu 24.04.4 LTS. Last booted 2026-10-01 21:26 |
| Public / private IP | `172.214.156.151` / `10.0.0.4` |
| SSH | `ssh -i ~/.ssh/isba4775_azure azureuser@172.214.156.151` (key only; passwords are off) |
| Firewall (NSG `vm-career-platformNSG`) | 22 from `157.242.208.190/32` (rules 300 and 1000) and from `172.88.241.93/32` (1010). **`Allow-HTTP-80` already exists at priority 315**, port 80 from `*` |
| App | `~/career-platform` at commit `0546382`. `.env` holds `DATABASE_URL=sqlite:///./data/career_platform.db`. The DB has the resume content (`Eleanor McGough`) |
| Python | `~/career-platform/.venv/bin/uvicorn` (uvicorn 0.54.0, CPython 3.12.3) |
| Right now | **The site is down.** Nothing listens on 8000 or 80, because the hand-started uvicorn didn't survive the reboot. `uvicorn.pid` still holds the dead PID `41409`. nginx isn't installed. `ufw` is inactive. No `career-platform` service exists yet |

## How the pieces fit

```
Visitor ──http :80──▶ Azure firewall (Allow-HTTP-80) ──▶ nginx :80 ──▶ uvicorn 127.0.0.1:8000 (systemd: career-platform, user azureuser)
                         (no rule for 8000)                               ├─ worker 1
                                                                          └─ worker 2
```

- **Boot:** systemd starts both nginx and `career-platform`.
- **Crash:** if a worker dies, uvicorn's parent process starts a new one while the other worker keeps serving. If the whole service dies, systemd restarts it after 3 seconds.
- **Port 8000** is closed twice over. uvicorn listens only on `127.0.0.1`, which can't be reached from outside the VM, and Azure has no rule that lets 8000 in.

## Global Constraints

- The service is named `career-platform` and runs as `User=azureuser`.
- Use the existing `~/career-platform` code, `.venv` and `data/career_platform.db` as they are. **Don't change any repo files and don't add tests.** The only new files are system config outside the repo: `/etc/systemd/system/career-platform.service` and `/etc/nginx/sites-available/career-platform`.
- uvicorn binds to `127.0.0.1:8000` only.
- The port 80 rule is `Allow-HTTP-80` at priority 320. You manage it in the portal yourself.
- No crash, kill or reboot tests. You'll run those yourself.
- Total running time is about 20 minutes.

## Review Focus

- **A leftover hand-started uvicorn holding port 8000.** The service would fail with "address already in use" and keep restarting. Task 1 confirms the port is free first.
- **Wrong working directory or missing `.env` silently serves an empty DB.** SQLite creates a new, empty file instead of failing, and the site still returns 200 with the fallback banner. Task 2 checks for your name, for a banner count of 0, and that no stray root `career_platform.db` exists.
- **nginx's default "Welcome to nginx" site answers instead of yours.** Task 3 removes the default site and checks for your name through port 80.
- **Port 8000 accidentally public.** That happens if uvicorn binds `0.0.0.0` and someone adds an 8000 rule. Task 2 checks the bind address, and Task 5 checks from the laptop that `:8000` times out.
- **The firewall rule's priority differs from the spec (315 versus 320).** Task 4 has you settle it in the portal.

---

### Task 1: Clear the hand-started leftovers

**What and why:** Before systemd takes over, make sure nothing else is using port 8000. Also delete the stale PID file from the old manual method so it can't confuse anyone later.

- [x] **Step 1: Confirm port 8000 is free and remove the stale PID file**
  - **Where:** VM (`ssh -i ~/.ssh/isba4775_azure azureuser@172.214.156.151`)
  - **Run:**
    ```bash
    sudo ss -ltnpH "sport = :8000"
    pgrep -af "[u]vicorn app.main" || echo "no uvicorn running"
    rm -f ~/career-platform/uvicorn.pid
    ```
  - **Check:** `ss` prints nothing, and the second line prints `no uvicorn running`. If a uvicorn *is* running, stop it first with `kill <PID>` and run the check again.
  - **Undo:** Nothing to undo. The PID file was already stale.

> **Executed 2026-10-01: complete.** Ran over SSH from the laptop as one command.
> - `ss` for port 8000 printed nothing, so the port is free.
> - `pgrep` first printed one match, but it was the SSH command's own `bash -c` line, because that line contains the text `uvicorn app.main`. Re-running with the pattern `[u]vicorn app.main` (the brackets stop it from matching itself) printed `no uvicorn running`. The Run block above now uses that pattern.
> - `uvicorn.pid` existed before (`-rw-rw-r--`, dated Sep 29 22:15, holding the dead PID 41409) and is gone after (`No such file or directory`).
> - The VM's `git status -s` shows only `?? data/career_platform.db.pre-resume.bak`. That's the backup from 2026-09-29, and it isn't touched here. No repo files changed.

### Task 2: Create the `career-platform` service (systemd)

**What and why:** A systemd "unit file" is a short recipe that tells Linux how to run a program: which user, which folder, which command, and what to do if it stops. `enable` makes it start at every boot. `Restart=always` brings it back after a crash. `--workers 2` runs two copies of the app under one parent, so if one crashes the other keeps serving while the parent replaces it. Two workers suit the VM's 2 vCPUs and fit easily in its memory.

The unit calls `.venv/bin/uvicorn` directly instead of `uv run`. systemd doesn't load your shell's PATH, and a full path can't pick up the wrong Python.

- [x] **Step 1: Write the unit file**
  - **Where:** VM
  - **Run:**
    ```bash
    sudo tee /etc/systemd/system/career-platform.service > /dev/null <<'EOF'
    [Unit]
    Description=career-platform website (FastAPI on uvicorn)
    After=network.target

    [Service]
    User=azureuser
    Group=azureuser
    WorkingDirectory=/home/azureuser/career-platform
    EnvironmentFile=/home/azureuser/career-platform/.env
    ExecStart=/home/azureuser/career-platform/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
    Restart=always
    RestartSec=3

    [Install]
    WantedBy=multi-user.target
    EOF
    ```
  - **What each line does:**
    - `User`/`Group` make the app run as `azureuser`, not root.
    - `WorkingDirectory` matters because the relative DB path, `static/` and `templates/` all resolve from it.
    - `EnvironmentFile` loads `DATABASE_URL` from `.env`.
    - `--host 127.0.0.1` keeps port 8000 private to the VM.
    - `WantedBy=multi-user.target` means "start at normal boot".
  - **Check:** `systemd-analyze verify /etc/systemd/system/career-platform.service` prints nothing, which means there are no errors.
  - **Undo:** `sudo rm /etc/systemd/system/career-platform.service && sudo systemctl daemon-reload`

- [x] **Step 2: Load, enable for boot, and start**
  - **Where:** VM
  - **Run:** `sudo systemctl daemon-reload && sudo systemctl enable --now career-platform`
  - **Check:**
    ```bash
    systemctl is-enabled career-platform                    # enabled  (starts at boot)
    systemctl is-active career-platform                     # active
    systemctl show -p Restart --value career-platform       # always
    ps -o user= -p "$(systemctl show -p MainPID --value career-platform)"   # azureuser
    pgrep -u root -af "uvicorn app.main" || echo "none as root"             # none as root
    journalctl -u career-platform -b --no-pager | grep -c "Application startup complete"   # 2 (one per worker)
    sudo ss -ltnpH "sport = :8000"                          # 127.0.0.1:8000 only, never 0.0.0.0
    ```
  - **Undo:** `sudo systemctl disable --now career-platform`

- [x] **Step 3: The app serves your data, not the fallback**
  - **Where:** VM
  - **Run:**
    ```bash
    curl -s http://127.0.0.1:8000/health
    curl -s http://127.0.0.1:8000/about | grep -c "Showing the latest saved profile snapshot"
    curl -s http://127.0.0.1:8000/about | grep -c "Eleanor McGough"
    ls ~/career-platform/career_platform.db 2>&1
    ```
  - **Check:** `{"status":"ok"}`, then `0` (no fallback banner), then a number ≥ 1, then `No such file or directory` (no stray empty DB).
  - **Undo:** Read-only.

> **Executed 2026-10-01: complete.** All three steps ran over SSH from the laptop, exactly as written. (Step 1 also had a guard that refused to overwrite an existing unit file; there wasn't one.)
> - Step 1: `/etc/systemd/system/career-platform.service` was written (owner root, `-rw-r--r--`, 409 bytes), and its contents match the plan. `systemd-analyze verify` printed nothing (exit 0).
> - Step 2: `enable --now` created the boot link `multi-user.target.wants/career-platform.service`. Results:
>   - `is-enabled` gives `enabled`, `is-active` gives `active`, and `Restart` gives `always`.
>   - The main process (PID 1934) runs as `azureuser`, and the root check printed `none as root`.
>   - The service has the parent uvicorn (1934), **2 workers** (1939, 1940), and Python's small `multiprocessing.resource_tracker` helper (1938). The helper is normal with `--workers` and isn't a third worker. All four run as `azureuser`.
>   - `Application startup complete` appears 2 times, and the journal shows `Started parent process [1934]` plus 2 `Started server process` lines.
>   - The listener is `127.0.0.1:8000` only, never `0.0.0.0`.
> - Step 3: `/health` returned `{"status":"ok"}`, the banner count was `0`, and `Eleanor McGough` appeared 3 times. There is no stray root `career_platform.db`. Also checked: `/resume`, `/portfolio` and `/contact` return `200`, and the journal has 0 `error`/`traceback` lines.
> - Memory: 375 MiB used and 511 MiB available on the 887 MiB VM. Each worker uses about 69 MB.
> - No repo files changed. The VM's `git status` still shows only the 2026-09-29 `.pre-resume.bak` backup.

### Task 3: Put nginx in front on port 80

**What and why:** Only root can open ports below 1024, such as 80. nginx is a small, standard web server that solves this. Its master process opens port 80 as root, and its worker processes, which handle the traffic, run as the unprivileged `www-data` user. nginx then *reverse-proxies*, meaning it forwards each request to uvicorn on `127.0.0.1:8000` and sends the answer back. Your app never needs root.

- [x] **Step 1: Install nginx**
  - **Where:** VM
  - **Run:** `sudo apt-get update && sudo apt-get install -y nginx`
  - **Check:** `systemctl is-enabled nginx` gives `enabled` and `systemctl is-active nginx` gives `active`. Ubuntu enables nginx at boot automatically. Note that `Allow-HTTP-80` is already open, so for a minute the public IP shows "Welcome to nginx".
  - **Undo:** `sudo apt-get purge -y nginx nginx-common && sudo apt-get autoremove -y` (if Step 2 ran, do its undo first)

- [x] **Step 2: Point nginx at the app and remove the default site**
  - **Where:** VM
  - **Run:**
    ```bash
    sudo tee /etc/nginx/sites-available/career-platform > /dev/null <<'EOF'
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    EOF
    sudo ln -s /etc/nginx/sites-available/career-platform /etc/nginx/sites-enabled/career-platform
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
    sleep 2   # added during execution: let the old nginx workers finish (see note below)
    ```
  - **What each part does:**
    - `default_server` plus `server_name _` means "answer every request to this IP".
    - The `proxy_set_header` lines pass along the original host and visitor IP. uvicorn trusts these headers from `127.0.0.1` by default, so your logs show real visitor IPs.
    - `sites-available` holds configs; `sites-enabled` holds links to the active ones.
  - **Check:** `nginx -t` prints `syntax is ok` and `test is successful`. Then:
    ```bash
    curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://127.0.0.1/   # 307 http://127.0.0.1/about
    curl -s http://127.0.0.1/about | grep -c "Eleanor McGough"                      # ≥ 1
    sudo ss -ltnpH "sport = :80"                                                     # nginx on 0.0.0.0:80 and [::]:80
    ```
  - **Undo:** `sudo rm /etc/nginx/sites-enabled/career-platform /etc/nginx/sites-available/career-platform && sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && sudo systemctl reload nginx`

> **Executed 2026-10-01: complete.** Both steps ran over SSH from the laptop.
> - Step 1: `apt-get update` and `apt-get install -y nginx` both exited 0. They ran non-interactively, with logs at `/tmp/apt-nginx-update.log` and `/tmp/apt-nginx-install.log` on the VM. Installed `nginx/1.24.0 (Ubuntu)`; `is-enabled` gives `enabled` and `is-active` gives `active`. Only `default` was in `sites-enabled`.
> - Step 2: The site file was written, with a guard that refused to overwrite an existing one; there wasn't one. The link was created and `default` was removed, so `sites-enabled` now holds only `career-platform`. `nginx -t` printed `syntax is ok` and `test is successful`, and the reload exited 0.
> - **First check run: mixed results, caused by a timing race and not a config problem.** `/` returned `200` instead of `307`, the name count was `0`, and `/resume`, `/portfolio`, `/contact` and `/health` returned `404`.
>   - Why: the checks ran within the same second as the reload (22:23:57). nginx reloads *gracefully*: it starts new workers with the new config and lets the old ones finish. For that moment, two old workers (started at install with the default site) were still answering. The nginx access log shows those 404s at 22:23:57 at 162 bytes, which is nginx's own default 404 page.
>   - What fixed it: nothing was changed. A second later the old workers had exited, and only the new workers 2704 and 2705 remained.
>   - Plan change: the Run block above now has `sleep 2` after the reload.
> - **Second check run, at 22:24:09, matching every Check:**
>   - `/` gives `307 http://127.0.0.1/about`.
>   - `/about`, `/resume`, `/portfolio`, `/contact` and `/health` all return `200`.
>   - `Eleanor McGough` appears 3 times, and the banner count is `0`.
>   - `ss` shows nginx on `0.0.0.0:80` and `[::]:80`.
>   - The nginx master runs as `root` and its workers as `www-data`. The app is still `127.0.0.1:8000`, all `azureuser`.
>   - The app log shows the proxied requests arriving from `127.0.0.1:0`, which confirms the forwarding headers are being read. The `0` is a placeholder port that uvicorn uses for forwarded clients.
> - Port 80 is already open to the Internet through the existing `Allow-HTTP-80` (priority 315), so the site should already be public. That gets checked in Task 5.

### Task 4: Firewall rule for port 80 (you, in the portal)

**What and why:** The Azure firewall (NSG) decides which traffic from the Internet reaches the VM. Visitors need port 80. Port 8000 gets **no** rule.

- [x] **Step 1: Set `Allow-HTTP-80` to the spec values**
  - **Where:** Azure portal, by you: VM → Networking → Inbound port rules.
  - **Do:** The rule already exists at **priority 315**. Open it and change the priority to **320**, keeping port 80, TCP, source Any, Allow. (Leaving it at 315 would also work, since nothing at a lower number blocks port 80. Editing it makes Azure match the spec.) Don't add any rule for 8000.
  - **Check (laptop, read-only):**
    ```bash
    az network nsg rule list -g rg-career-platform --nsg-name vm-career-platformNSG \
      --query "sort_by([],&priority)[].{name:name,pri:priority,port:destinationPortRange,src:sourceAddressPrefix}" -o table
    ```
    The output shows `Allow-HTTP-80  320  80  *`, and no row has port `8000`.
  - **Undo:** Set the priority back to 315, or delete the rule to take the site off the Internet.

> **Executed 2026-10-01: complete.** The user changed `Allow-HTTP-80` from priority 315 to 320 in the portal. Claude ran the read-only check from the laptop:
> - `Allow-HTTP-80  320  80  TCP  *  Allow  Inbound`, which matches the spec.
> - The other rules are unchanged: `Allow-SSH-Laptop` (300), `AllowSSHFromLaptop` (1000) and `AllowSSHFromHome` (1010), all port 22 from a single `/32` address.
> - No rule allows port `8000`. `vm-career-platformNSG` is the only NSG in `rg-career-platform` (checked 2026-10-01), and it's attached to the VM's NIC.

### Task 5: Check it from the Internet

**What and why:** Everything so far was tested from inside the VM. This task proves a real visitor can reach the site and can't reach port 8000.

- [x] **Step 1: Site on port 80, port 8000 closed**
  - **Where:** laptop
  - **Run:**
    ```bash
    curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://172.214.156.151/
    for p in /about /resume /portfolio /contact /health; do printf '%s ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' "http://172.214.156.151$p"; done
    curl -s http://172.214.156.151/about | grep -c "Showing the latest saved profile snapshot"
    curl -s -m 5 -o /dev/null -w '%{http_code}\n' http://172.214.156.151:8000/health
    ```
  - **Check:**
    - `307 http://172.214.156.151/about`.
    - All five paths print `200`.
    - The banner count is `0`.
    - The last command prints `000` after about 5 seconds, which is a timeout, meaning 8000 is closed.
  - **Then:** open `http://172.214.156.151` in a browser. It should land on your About page with no port number in the address bar.
  - **Undo:** Read-only.

> **Executed 2026-10-01: complete.** Ran from the laptop (laptop IP `157.242.208.190`) against the public IP.
> - `/` gives `307 http://172.214.156.151/about`. Following it (`curl -L`) ends at `200 http://172.214.156.151/about`.
> - `/about`, `/resume`, `/portfolio`, `/contact` and `/health` all return `200`. The banner count is `0`, and `Eleanor McGough` appears 3 times. The page's CSS file under `/static/` returns `200`.
> - `http://172.214.156.151:8000/health` printed `000` with curl exit `28`, a timeout after 5 seconds (16:33:09 to 16:33:14). **Port 8000 is closed to the Internet.**
> - VM afterwards:
>   - The app journal shows the requests from `157.242.208.190`, which is the real visitor IP, passed along by nginx.
>   - There are 0 `error`/`traceback` lines in the app journal and 0 non-notice lines in the nginx error log.
>   - `career-platform` and `nginx` are both `enabled` for boot.
>   - There is no stray root `career_platform.db`.
> - **Left for the user:** the visual check in a browser at `http://172.214.156.151`, and the crash, worker-kill and reboot tests.

---

## After this plan

- **Updating the site later (VM):** run `cd ~/career-platform && git pull --ff-only && uv sync --locked && sudo systemctl restart career-platform`.
- **Logs (VM):** run `journalctl -u career-platform -f` for the app and `sudo tail -f /var/log/nginx/access.log` for visits.
- **Your own tests:** the crash, worker-kill and reboot tests are yours to run. For a reboot test, `systemctl is-enabled` showing `enabled` for both `career-platform` and `nginx` is what makes the site come back on boot.

## Full rollback (reverse order)

1. Portal: delete or edit `Allow-HTTP-80` (Task 4 undo).
2. VM: `sudo rm -f /etc/nginx/sites-enabled/career-platform /etc/nginx/sites-available/career-platform && sudo apt-get purge -y nginx nginx-common && sudo apt-get autoremove -y`. The site files are removed by hand because purge only deletes files that came with the package.
3. VM: `sudo systemctl disable --now career-platform && sudo rm /etc/systemd/system/career-platform.service && sudo systemctl daemon-reload`.
4. The repo isn't touched, so there is nothing to revert in git.
