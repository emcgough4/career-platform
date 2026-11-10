# AWS EC2 and RDS Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. As each section finishes, tick its boxes and add an `> **Executed YYYY-MM-DD: …**` note under it, the same way the earlier plans do. Also log every deviation from the plan in `docs/migration-notes.md` (course guide, section 9).

**Goal:** Serve elliemcgough.me from an EC2 instance in us-east-1, backed by a Single-AZ RDS PostgreSQL 18 database. Test it first at `aws.elliemcgough.me`, with Railway kept running unchanged as the rollback.

**Architecture:** The app code stays the same FastAPI + SQLAlchemy app. On one `t3.micro` Ubuntu 26.04 instance, nginx terminates HTTPS (Certbot, Let's Encrypt) and proxies to uvicorn on `127.0.0.1:8000`, run by systemd as an unprivileged `career-app` user. The app connects to a private, encrypted `db.t4g.micro` RDS instance over TLS (`verify-full`) as a read-only role. Migrations run as the owner role, only from a deploy script. The data moves once: a `pg_dump` from Railway is restored **from the EC2 instance** with Ubuntu 26.04's Postgres 18 client. The copy is tested at `aws.elliemcgough.me`, then Cloudflare's apex record moves from Railway to the instance's Elastic IP.

**Tech Stack:** AWS CLI v2 (profile `isba-4775`), EC2, Elastic IP, RDS for PostgreSQL 18.6, Ubuntu 26.04 (`postgresql-client` 18, system `python3`), nginx, Certbot, systemd, uv 0.12.19, FastAPI, uvicorn, SQLAlchemy 2.1, Alembic, psycopg 3, Railway CLI, Cloudflare DNS and the `cf` CLI.

**Spec:** The request in chat on 2026-11-03: "Look at my app and help me plan its move to AWS. Use EC2 for the app and a Single-AZ RDS PostgreSQL database. Work on a new branch so Railway doesn't redeploy from main. Don't create anything yet." Decisions from the interview that day:
- The domain moves to AWS.
- The account is the user's alone.
- The cutover allows a few minutes of downtime.
- Later the same day: **"follow course's guide"**, meaning `LMU-ISBA/isba-4775-fa26/guides/aws-migration.md` (sections 7–12) for sizing, image, restore path, the test subdomain and the merge to `main`.

The constraints come from the course policy `guides/aws-ec2-deployment-policy.json`.

## What's there today (found 2026-11-03, read-only)

| Item | Value |
| --- | --- |
| Live site | `https://elliemcgough.me`, `server: railway-hikari`. Apex is a DNS-only CNAME to `tmbs117o.up.railway.app`. `www` is a proxied placeholder (`192.0.2.1`) that a Cloudflare rule 301s to the apex (`docs/evidence/dns-https-final.md`). MX/SPF/DKIM/DMARC/Zoho TXT records are for mail and must not change. |
| Railway DB | PostgreSQL 18.6, private network only. Backup method: `railway ssh -s Postgres` → `pg_dump -Fc` (memory `railway-postgres-backup-method`). Last dump: `backups/railway-postgres-20261029T215819Z.dump` |
| App | 6 GET routes plus `/health` (no DB). **No write paths**: no POST/PUT/DELETE, no `commit()`. On a DB error the pages return **503** with the snapshot and the marker `<!-- Showing the latest saved profile snapshot. -->` |
| Config | `DATABASE_URL` → `app/config.py` (`postgres(ql)://` rewritten to `postgresql+psycopg://`). `alembic/env.py` passes it to `config.set_main_option`, which is a configparser call, so a `%` in the URL (URL-encoded password) raises `ValueError` |
| Python | `.python-version` is `3.12` (Railway reads it, so it stays). `uv.lock` has x86_64 Linux wheels for 3.12–3.14 for every compiled dependency (psycopg-binary, pydantic-core, httptools, uvloop, watchfiles) |
| Railway-only pieces | `railway.json` (preDeploy `alembic upgrade head`, `--forwarded-allow-ips=*`, `/health` check, restart policy), `railpack.json`, `tests/test_railway_config.py`. **They stay as they are** so Railway keeps working as the rollback |
| AWS account `909096719723` | **Free plan** (confirmed by `FreeTierRestrictionError`, Section 3 Step 5). Default VPC `vpc-02ed278a349b93372` (`172.31.0.0/16`), six default public subnets (us-east-1a `subnet-091fafd64394acaf2`, b `subnet-0dbd1bce00600192f`, c `subnet-0b1960fc8f1fe3b0d`, d `subnet-0c624206cd7096d5f`, e `subnet-088369ecdfbb283bb`, f `subnet-006a7c5373439e854`) |
| Ubuntu image | SSM `/aws/service/canonical/ubuntu/server/26.04/stable/current/amd64/hvm/ebs-gp3/ami-id` was `ami-0bfc5cae5711ffac8` (`ubuntu-resolute-26.04-amd64-server-20261028`, owner Canonical `099720109477`, root `/dev/sda1`, 8 GB default, `UsageOperation: RunInstances`, so not Pro-billed). Look it up again at launch |
| Laptop | `uv 0.12.19`, Homebrew `postgresql@18 18.6_1`, `~/.ssh/isba4775_azure` (Azure key, not reused). `env/` and `backups/` are git-ignored |
| Repo | `https://github.com/emcgough4/career-platform`, public |

## Policy and Free-plan rules this plan must satisfy

- Region `us-east-1` only. EC2 `t3.micro`/`t3.small` only. `HttpTokens=required` at launch.
- RDS `db.t3.micro`/`db.t4g.micro`, not Multi-AZ, ≤ 20 GB, encrypted, never publicly accessible. **Pass `--storage-encrypted` and `--no-publicly-accessible` explicitly**: the policy's Denies use `BoolIfExists`, so leaving the flags out can be denied.
- Not allowed: VPC changes, `ModifyInstanceAttribute` (no resizing, no swapping security groups on a running instance), `CreateKeyPair` (import only), `iam:PassRole` (no instance role, so no Secrets Manager, SSM Session Manager or CloudWatch agent), and Secrets Manager–managed RDS passwords.
- Free plan: RDS backup retention of **1 day at most** (found in Section 3 Step 5). Don't upgrade the account plan (course guide, section 1).

## Global Constraints

- Every AWS command runs with `export AWS_PROFILE=isba-4775 AWS_REGION=us-east-1` set first. (zsh doesn't word-split `$VAR`, so don't put flags in a variable.)
- Names:
  - Key pair `isba4775-aws`.
  - Security groups `career-platform-web` and `career-platform-db`.
  - Instance and Elastic IP: tag `Name=career-platform`.
  - DB subnet group and DB instance `career-platform-db`.
  - Database `career_platform`, owner role `career_admin`, app role `career_app`.
  - Test hostname `aws.elliemcgough.me`.
- Instance: **`t3.micro`, Ubuntu Server 26.04 LTS (x86_64), On-Demand, Standard CPU credits, 20 GB encrypted gp3, IMDSv2 required** (course guide, section 8).
- AZ `us-east-1a` for both the instance and the database (no cross-AZ traffic).
- Values found at run time are written into the Executed notes as `<AMI_ID>`, `<INSTANCE_ID>`, `<WEB_SG>`, `<DB_SG>`, `<EIP>`, `<EIP_ALLOC>`, `<RDS_HOST>`. IDs and the Elastic IP may be recorded; `<HOME_IP>` and `<SCHOOL_IP>` are not. **Passwords, full `DATABASE_URL`s and dumps never go into the repo, the plan or chat.**
- Passwords: `openssl rand -hex 24` (hex only, so nothing needs URL-encoding). Stored on the laptop in `~/.config/career-platform/rds-master-password` and `~/.config/career-platform/rds-app-password`, mode 600, outside the repo.
- Server layout:
  - Code: `/opt/career-platform` (owner `ubuntu`).
  - App env: `/etc/career-platform/app.env` (`root:career-app`, 0640).
  - Migration env: `/etc/career-platform/migrate.env` (`ubuntu:ubuntu`, 0600).
  - RDS CA: `/etc/ssl/certs/rds-global-bundle.pem`.
- Both `DATABASE_URL`s end in `?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5`. libpq tools (`psql`, `pg_restore`) accept the same URL.
- Python comes from Ubuntu's `/usr/bin/python3` (`UV_PYTHON=/usr/bin/python3 UV_PYTHON_PREFERENCE=only-system`), overriding `.python-version`. Never use a uv-managed Python under `~ubuntu`, because `career-app` can't read `/home/ubuntu`.
- Code work happens on branch `aws-ec2-rds-migration`. **Don't push to `main` or open a PR before cutover** (a PR can trigger a Railway preview deploy). Ask before the one `git push -u origin aws-ec2-rds-migration` in Section 2. The merge to `main` comes after cutover (Section 9).
- Don't run the Azure deploy steps or `scripts/*.sql` on AWS (course guide, section 9).
- Railway's service, variables, custom domain and `railway.json` are not changed by this plan.
- **Content freeze** from Section 5 Step 1 until Section 8 is done. No edits to Railway's database in that time.
- Local tests keep using SQLite. No test needs AWS or Postgres.

## Review Focus

- **`%` in a database URL crashes Alembic.** `set_main_option` is configparser, and `%40` reads as interpolation. Task 2 escapes it and tests offline migration with an encoded password.
- **uvicorn trusting every forwarded header.** Railway needs `--forwarded-allow-ips=*`; on EC2 it lets anyone fake `X-Forwarded-Proto` and the client IP. Task 1 tests that the unit binds `127.0.0.1` and doesn't pass that flag. Sections 7 and 8 check `og:image` is `https://`.
- **A DB outage that hangs instead of falling back.** With no `connect_timeout`, a blocked RDS connection waits about 2 minutes per request. Task 2 pins the URL query. Section 7 Step 4 blocks the DB and expects a 503 with the marker within a few seconds, then recovery once it's unblocked.
- **The wrong Python, or one the app user can't read.** `.python-version` asks for 3.12, which 26.04 may not ship. Without the override, uv either fails or downloads 3.12 into `~ubuntu/.local`, and `career-app` then gets "permission denied" at start. Task 1's deploy script sets `UV_PYTHON=/usr/bin/python3` and `UV_PYTHON_PREFERENCE=only-system`. Section 4 Step 3 checks `readlink -f .venv/bin/python` starts with `/usr/bin/python3`.
- **Certbot editing a tracked file.** `certbot --nginx` rewrites the site config. The config is copied into `/etc/nginx`, not symlinked, so the repo copy on the server stays clean (`git status` checked in Section 7).

---

## 1. Code: EC2 deploy files (Task 1)

### Task 1: systemd unit, nginx site and deploy script for EC2

**Files:**
- Create: `deploy/aws/career-platform.service`
- Create: `deploy/aws/nginx-career-platform.conf`
- Create: `deploy/aws/deploy.sh` (mode 755)
- Test: `tests/test_aws_deploy_config.py`

**Interfaces:**
- Consumes: `/health` route (`app/main.py`), env file paths from Global Constraints.
- Produces: `deploy/aws/deploy.sh [git-ref]`, run on the server as `ubuntu` from any directory. It exits 0 only if `/health` returns `{"status":"ok"}` and `/about` returns 200 (not 503) after the restart. Sections 6 and 9 call it.

- [x] **Step 1: Write the failing tests** in `tests/test_aws_deploy_config.py`. They read the three files as text from `DEPLOY = REPO_ROOT / "deploy" / "aws"` through a small `read(name)` helper:

```python
def test_unit_runs_uvicorn_on_loopback_without_trusting_all_proxies():
    unit = read("career-platform.service")
    exec_start = next(line for line in unit.splitlines() if line.startswith("ExecStart="))
    assert "/opt/career-platform/.venv/bin/uvicorn app.main:app" in exec_start
    assert "--host 127.0.0.1" in exec_start and "--port 8000" in exec_start and "--workers 2" in exec_start
    assert "0.0.0.0" not in unit and "--forwarded-allow-ips" not in unit

def test_unit_runs_as_app_user_with_app_env():
    unit = read("career-platform.service")
    for line in ["User=career-app", "Group=career-app", "WorkingDirectory=/opt/career-platform",
                 "EnvironmentFile=/etc/career-platform/app.env", "Restart=always", "WantedBy=multi-user.target"]:
        assert line in unit.splitlines()
    assert "migrate.env" not in unit

def test_nginx_proxies_to_loopback_for_test_and_real_names():
    conf = read("nginx-career-platform.conf")
    assert "listen 80 default_server;" in conf
    assert "server_name aws.elliemcgough.me elliemcgough.me;" in conf
    assert "proxy_pass http://127.0.0.1:8000;" in conf
    for header in ["Host $host", "X-Forwarded-For $proxy_add_x_forwarded_for", "X-Forwarded-Proto $scheme"]:
        assert f"proxy_set_header {header};" in conf

def test_deploy_script_syncs_then_migrates_as_owner_then_restarts_then_checks():
    script = read("deploy.sh")
    assert script.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    steps = ["UV_PYTHON=/usr/bin/python3", "UV_PYTHON_PREFERENCE=only-system", "uv sync --locked",
             "/etc/career-platform/migrate.env", "alembic upgrade head", "systemctl restart career-platform",
             "/health", "/about"]
    positions = [script.index(step) for step in steps]
    assert positions == sorted(positions)

def test_deploy_script_is_executable():
    assert os.access(DEPLOY / "deploy.sh", os.X_OK)
```

- [x] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_aws_deploy_config.py -v`
Expected: 5 FAIL with `FileNotFoundError` (no `deploy/aws/`).

- [x] **Step 3: Write the three files**
  - `career-platform.service`: the Azure unit from `2026-10-01-operate-the-vm.md` Task 2, with the user, paths and env file above, `After=network-online.target` and `Wants=network-online.target`, and `RestartSec=3`. Two workers: a `t3.micro` has 2 vCPUs, and the Azure VM ran two workers in about 140 MB of RAM.
  - `nginx-career-platform.conf`: one `server` block on port 80 (`listen 80 default_server;`, `listen [::]:80 default_server;`, `server_name aws.elliemcgough.me elliemcgough.me;`), with `location /` proxying as in the tests. Certbot adds the 443 block in Section 7.
  - `deploy.sh`:
    1. `cd /opt/career-platform`, then `git fetch origin` and `git checkout --detach "${1:-origin/aws-ec2-rds-migration}"`.
    2. `UV_PYTHON=/usr/bin/python3 UV_PYTHON_PREFERENCE=only-system uv sync --locked`.
    3. In a subshell: `set -a; . /etc/career-platform/migrate.env; set +a; .venv/bin/alembic upgrade head`.
    4. `sudo systemctl restart career-platform`.
    5. Poll `curl -fsS http://127.0.0.1:8000/health` up to 15 times, one second apart.
    6. Require `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/about` to be `200`. Print a one-line summary with the deployed commit (`git rev-parse --short HEAD`).

- [x] **Step 4: Run the tests to see them pass**

Run: `uv run pytest -q`
Expected: all pass (5 new).

- [x] **Step 5: Commit**

```bash
git add deploy/aws tests/test_aws_deploy_config.py
git commit -m "feat: add the systemd unit, nginx site and deploy script for EC2"
```

> **Executed 2026-11-05: complete (`386051f`).** Followed the plan as written.
> - The 5 tests failed first: 4 with `FileNotFoundError` and 1 on `os.access`. After the three files were written, the suite was 53 passed.
> - `bash -n deploy/aws/deploy.sh` reports no syntax errors.

## 2. Code: database URL safety (Task 2)

### Task 2: Alembic accepts `%` in the URL; the RDS query string survives

**Files:**
- Modify: `alembic/env.py` (the `set_main_option` line)
- Modify: `.env.example` (comment showing the RDS URL shape with placeholders)
- Test: `tests/test_alembic_env.py`, `tests/test_config.py`

**Interfaces:**
- Consumes: `normalize_database_url(url: str) -> str` (unchanged).
- Produces: nothing new. `alembic upgrade head` works for any valid URL.

- [x] **Step 1: Write the failing test** in `tests/test_alembic_env.py`. Use the subprocess pattern from `tests/test_config.py`:

```python
def test_offline_migration_accepts_percent_encoded_password():
    env = {**os.environ, "DATABASE_URL": "postgresql://u:p%40ss@db.example:5432/career_platform"}
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
                            cwd=REPO_ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "CREATE TABLE profiles" in result.stdout
```

Add this case to the `test_normalize_database_url` parametrize list in `tests/test_config.py`. It passes already; it guards the query string:
`("postgresql://u:p@h:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5", "postgresql+psycopg://u:p@h:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5")`

- [x] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_alembic_env.py -v`
Expected: FAIL, with stderr containing `invalid interpolation syntax`.

- [x] **Step 3: Escape `%` as `%%`** in `alembic/env.py`: `config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))`, plus a one-line comment saying why. Add the `.env.example` comment:
  `# AWS (EC2 → RDS): postgresql://career_app:<password>@<rds-host>:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5`

- [x] **Step 4: Run the tests to see them pass**

Run: `uv run pytest -q`
Expected: all pass.

- [x] **Step 5: Commit, then push the branch (ask first)**

```bash
git add alembic/env.py .env.example tests/test_alembic_env.py tests/test_config.py
git commit -m "fix: let Alembic accept percent-encoded database URLs"
git push -u origin aws-ec2-rds-migration   # only after the user says yes
```
Check: `git log origin/main..origin/aws-ec2-rds-migration --oneline` lists this plan's commits, and `origin/main` has not moved. Railway shows no new deployment.

> **Executed 2026-11-05: complete (`e1010c2`).** Followed the plan as written.
> - The test failed first with `ValueError: invalid interpolation syntax … at position 24`. After the `%%` escape, the suite was 55 passed.
> - `alembic current` against the local SQLite file still prints `0002_project_category (head)`.
> - Pushed 2026-11-05 with the user's approval (branch head `ceaf1ed`). `origin/main` didn't move and Railway made no new deployment.

## 3. AWS resources (laptop, AWS CLI)

**Everything here is billed against the Free plan credits.** Ask the user before Step 3. Each step's Undo is listed again in reverse order under Rollback.

- [ ] **Step 1: Generate and import the SSH key, and generate passwords**
  - **Run:**
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/isba4775_aws -C isba4775-aws -N ''
    aws ec2 import-key-pair --key-name isba4775-aws --public-key-material fileb://$HOME/.ssh/isba4775_aws.pub \
      --tag-specifications 'ResourceType=key-pair,Tags=[{Key=Name,Value=isba4775-aws}]'
    umask 077; openssl rand -hex 24 > ~/.config/career-platform/rds-master-password; openssl rand -hex 24 > ~/.config/career-platform/rds-app-password
    ```
  - **Check:** `aws ec2 describe-key-pairs --key-names isba4775-aws` shows `KeyType: ed25519`. `ls -l ~/.config/career-platform/` shows `-rw-------` for both password files.
  - **Undo:** `aws ec2 delete-key-pair --key-name isba4775-aws`

> **Executed 2026-11-03: complete (in two parts).**
> - **Passwords**, before the database was created: they live in `~/.config/career-platform/` (directory 700, files 600, 48 hex characters each), outside the repository as the course guide asks, instead of the git-ignored `env/`. They were never printed.
> - **SSH key**, before the launch:
>   - Generated on the laptop as `~/.ssh/isba4775_aws` (600) and `.pub` (644). No file existed with that name before.
>   - Imported as `isba4775-aws` (`key-01ff8653df9a0b993`, `ed25519`). The private key never left the laptop.

- [x] **Step 2: Security groups**
  - **Run:** Get `<HOME_IP>` with `curl -s https://checkip.amazonaws.com`. Create `career-platform-web` in `vpc-02ed278a349b93372` with these inbound rules:
    - tcp 22 from `<HOME_IP>/32` (description `home`)
    - tcp 80 and 443 from `0.0.0.0/0`

    Create `career-platform-db` with one inbound rule: tcp 5432 from `UserIdGroupPairs=[{GroupId=<WEB_SG>}]`. Use `create-security-group --query GroupId --output text` and `authorize-security-group-ingress --ip-permissions …`. Add `<SCHOOL_IP>/32` (description `school`) the first time you're on campus, with the same command.
  - **Why:** SSH only from your IPs, as on Azure. The database only accepts the web server's security group, never an IP range.
  - **Check:** `aws ec2 describe-security-groups --group-ids <WEB_SG> <DB_SG> --query 'SecurityGroups[].IpPermissions'` shows exactly those rules, with no `0.0.0.0/0` on 22 or 5432.
  - **Undo:** `aws ec2 delete-security-group --group-id <DB_SG>`, then the same for `<WEB_SG>`.

> **Executed 2026-11-03: complete.** Created before Sections 1–2, because the course guide's section 7 creates both groups along with the database.
> - `<WEB_SG>` = `sg-0e35c236b5e8b76c1` (`career-platform-web`). Inbound rules:
>   - tcp 22 from `<HOME_IP>/32`, description `laptop-2026-11-03`. The address isn't recorded here.
>   - tcp 80 from `0.0.0.0/0`.
>   - tcp 443 from `0.0.0.0/0`.
> - `<DB_SG>` = `sg-0d2918f4b6db4e9a3` (`career-platform-db`). Inbound rule: tcp 5432 from `sg-0e35c236b5e8b76c1` only.
> - Check: `describe-security-groups` shows exactly these rules, with no `0.0.0.0/0` on 22 or 5432.

- [x] **Step 3: Launch the instance (dry run first)**
  - **Run:**
    ```bash
    AMI_ID=$(aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/26.04/stable/current/amd64/hvm/ebs-gp3/ami-id --query Parameter.Value --output text)
    aws ec2 describe-images --image-ids "$AMI_ID" --query 'Images[0].[Name,OwnerId,RootDeviceName,UsageOperation]' --output text
    aws ec2 run-instances --dry-run --image-id "$AMI_ID" --instance-type t3.micro --key-name isba4775-aws \
      --subnet-id subnet-091fafd64394acaf2 --security-group-ids sg-0e35c236b5e8b76c1 \
      --metadata-options HttpTokens=required,HttpEndpoint=enabled,HttpPutResponseHopLimit=1 \
      --credit-specification CpuCredits=standard \
      --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}' \
      --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=career-platform}]' 'ResourceType=volume,Tags=[{Key=Name,Value=career-platform-root}]'
    ```
    1. Check the image: `describe-images` must show a name containing `ubuntu-resolute-26.04-amd64-server` (not `pro-server`), owner `099720109477`, root `/dev/sda1` and `RunInstances`.
    2. The dry run should print `DryRunOperation`.
    3. Rerun the same command without `--dry-run`, adding `--query 'Instances[0].InstanceId' --output text`.
    4. Run `aws ec2 wait instance-status-ok --instance-ids <INSTANCE_ID>`.
  - **Before first SSH:** compare the host key fingerprints in `aws ec2 get-console-output --instance-id <INSTANCE_ID> --latest --output text` (the `-----BEGIN SSH HOST KEY FINGERPRINTS-----` block) with what `ssh` shows on first connect (course guide, section 8).
  - **Check:** `describe-instances` shows `t3.micro`, `running`, `MetadataOptions.HttpTokens: required`, AZ `us-east-1a`, and a 20 GB encrypted root volume. `describe-instance-credit-specifications` shows `standard`. If `Encrypted=true` is denied (KMS), record it and rerun with `Encrypted=false`.
  - **Undo:** `aws ec2 terminate-instances --instance-ids <INSTANCE_ID>`

> **Executed 2026-11-03: complete.**
> - **Image:** `<AMI_ID>` = `ami-0bfc5cae5711ffac8`, `ubuntu/images/hvm-ssd-gp3/ubuntu-resolute-26.04-amd64-server-20261028`, owner `099720109477`, root `/dev/sda1`, `RunInstances` (not Pro).
> - **Dry run:** `DryRunOperation: Request would have succeeded`.
> - **Instance:** `<INSTANCE_ID>` = `i-08b123d5a33f3a6eb`. `instance-status-ok` took 3 min 26 s.
> - **Settings checked:**
>   - `t3.micro`, `running`, `us-east-1a`.
>   - `HttpTokens: required`, hop limit 1.
>   - Security group `career-platform-web`, key `isba4775-aws`, no instance profile.
>   - CPU credits `standard`.
>   - Root volume `vol-02d8b816f9d9fc173`: 20 GB `gp3`, `Encrypted: true` (no KMS denial), `DeleteOnTermination: true`.
> - **Host key:** the three fingerprints in `get-console-output --latest` (ECDSA `SHA256:FWl0FYI1…`, ED25519 `SHA256:jogwpQ3B…`, RSA `SHA256:+YTHbXOe…`) matched `ssh-keyscan` of the Elastic IP exactly. Only then were they added to `~/.ssh/known_hosts`, and the first SSH used `StrictHostKeyChecking=yes`.
> - **On the server:**
>   - `Ubuntu 26.04.1 LTS`.
>   - **Python 3.14.4**, which is in `uv.lock`'s 3.12–3.14 wheel range.
>   - 908 MiB RAM with 588 MiB available, 2 vCPUs, and 17 GB free on `/`.
>   - `postgresql-client` candidate `18+290ubuntu1`, not yet installed (Section 4 Step 1).

- [x] **Step 4: Elastic IP**
  - **Run:** `allocate-address --domain vpc --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=career-platform}]'`, then `associate-address --instance-id <INSTANCE_ID> --allocation-id <EIP_ALLOC>`.
  - **Why:** The address survives stop and start, so the Cloudflare records keep working. It bills while idle too, so release it at teardown.
  - **Check:** `ssh -i ~/.ssh/isba4775_aws ubuntu@<EIP> 'lsb_release -ds; curl -s -o /dev/null -w "%{http_code}\n" http://169.254.169.254/latest/meta-data/'` prints `Ubuntu 26.04…`, then `401` (IMDSv1 refused).
  - **Undo:** `disassociate-address --association-id …`, then `release-address --allocation-id <EIP_ALLOC>`.

> **Executed 2026-11-03: complete.**
> - `<EIP>` = `52.71.186.61`, `<EIP_ALLOC>` = `eipalloc-0a6c7030f9eb097fa`, association `eipassoc-0b858812160b85856`.
> - `describe-instances` shows the instance's public IP is the Elastic IP, and `describe-addresses` lists only this one address.
> - Check over SSH: `lsb_release` printed `Ubuntu 26.04.1 LTS`, and the metadata request without a token returned `401` (IMDSv1 refused).

- [x] **Step 5: DB subnet group and the RDS instance**
  - **Run:**
    ```bash
    aws rds create-db-subnet-group --db-subnet-group-name career-platform-db \
      --db-subnet-group-description "career-platform: default VPC subnets" \
      --subnet-ids subnet-091fafd64394acaf2 subnet-0dbd1bce00600192f subnet-0b1960fc8f1fe3b0d subnet-0c624206cd7096d5f subnet-088369ecdfbb283bb subnet-006a7c5373439e854
    aws rds create-db-instance --db-instance-identifier career-platform-db \
      --engine postgres --engine-version 18.6 --db-instance-class db.t4g.micro \
      --allocated-storage 20 --storage-type gp3 --storage-encrypted --no-multi-az --no-publicly-accessible \
      --availability-zone us-east-1a --db-subnet-group-name career-platform-db --vpc-security-group-ids <DB_SG> \
      --db-name career_platform --master-username career_admin --master-user-password "$(cat ~/.config/career-platform/rds-master-password)" \
      --backup-retention-period 1 --deletion-protection --copy-tags-to-snapshot \
      --tags Key=Name,Value=career-platform-db
    aws rds wait db-instance-available --db-instance-identifier career-platform-db   # about 10–15 min
    ```
  - **Why:**
    - No `--max-allocated-storage`, so storage autoscaling stays off and the 20 GB cap holds.
    - 18.6 matches Railway, so the 18 dump restores as is.
    - `--deletion-protection` stops an accidental delete.
  - **Check:** `describe-db-instances --query 'DBInstances[0].[Endpoint.Address,EngineVersion,DBInstanceClass,MultiAZ,PubliclyAccessible,StorageEncrypted,AllocatedStorage,MaxAllocatedStorage]'` gives `<RDS_HOST>`, `18.6`, `db.t4g.micro`, `false`, `false`, `true`, `20`, `None`.
  - **Undo:** Section 10 (teardown). Deletion protection must be turned off first.

> **Executed 2026-11-03: create request accepted. Not yet confirmed `available`.**
> - **Subnet group:** `career-platform-db` covers all six default subnets (us-east-1a to f), status `Complete`.
> - **Password handling:** the create call used `--cli-input-json` from a temporary 600-mode file in the scratchpad, deleted straight after, so the password never appeared in a command line or in output.
> - **Backup retention is 1 day, not 7** (a deviation from the plan and the course guide):
>   - 7 days failed with `FreeTierRestrictionError: The specified backup retention period exceeds the maximum available to free tier customers`.
>   - 6 down to 2 failed the same way. 1 day was accepted. Rejected requests created nothing.
>   - The only way to get more is to upgrade the account plan, which the course guide says not to do.
>   - This error also confirms the account is on the **Free plan**.
>   - Consequence: point-in-time restore only reaches back 1 day. Railway, plus the dumps in `backups/`, remain the longer-term copies.
> - **Create response:** `creating`, `db.t4g.micro`, `18.6`, `us-east-1a`, `MultiAZ: false`, `PubliclyAccessible: false`, `StorageEncrypted: true`, `20` GB `gp3`, `MaxAllocatedStorage: null` (autoscaling off), `BackupRetentionPeriod: 1`, `DeletionProtection: true`, security group `sg-0d2918f4b6db4e9a3`.
> - **Not waited on**, as the course guide suggests.
> - **Later the same day, after the EC2 launch:** status `available`. `<RDS_HOST>` = `career-platform-db.ccjwoiuqy9dz.us-east-1.rds.amazonaws.com`, `BackupRetentionPeriod: 1`, `PubliclyAccessible: false`.

## 4. Server setup (SSH as `ubuntu`)

- [x] **Step 1: Packages, app user, uv**
  - **Run:**
    ```bash
    sudo apt-get update && sudo apt-get -y upgrade
    sudo apt-get install -y git nginx certbot python3-certbot-nginx postgresql-client
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin career-app
    curl -LsSf https://astral.sh/uv/0.12.19/install.sh | sh && source ~/.local/bin/env
    [ -f /var/run/reboot-required ] && sudo reboot
    ```
  - **Check:**
    - `pg_restore --version` prints `18.x` (it must be 18 or newer to read Railway's dump).
    - `python3 --version` prints a version from 3.12 to 3.14. Record it.
    - `uv --version` prints `uv 0.12.19`.
    - `id career-app` works.
    - `nginx -v` and `certbot --version` print versions.
  - **Undo:** `sudo userdel career-app`. The packages can stay.

- [x] **Step 2: Clone the branch and fetch the RDS CA bundle**
  - **Run:**
    ```bash
    sudo install -d -o ubuntu -g ubuntu -m 755 /opt/career-platform
    git clone --branch aws-ec2-rds-migration https://github.com/emcgough4/career-platform.git /opt/career-platform
    sudo curl -fsSL -o /etc/ssl/certs/rds-global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
    ```
  - **Check:** `git -C /opt/career-platform log -1 --oneline` matches the laptop's branch head. `grep -c 'BEGIN CERTIFICATE' /etc/ssl/certs/rds-global-bundle.pem` is > 1.
  - **Undo:** `sudo rm -rf /opt/career-platform /etc/ssl/certs/rds-global-bundle.pem`

- [x] **Step 3: Python environment from the lock file and the system Python**
  - **Run:** `cd /opt/career-platform && UV_PYTHON=/usr/bin/python3 UV_PYTHON_PREFERENCE=only-system uv sync --locked && uv run --no-sync pytest -q`
  - **Check:**
    - `readlink -f .venv/bin/python` starts with `/usr/bin/python3`.
    - All tests pass (they use SQLite). If any fail only on the newer Python, stop and log it in `docs/migration-notes.md`.
    - `sudo -u career-app /opt/career-platform/.venv/bin/python -c 'import app.main'` exits 0.
  - **Undo:** `rm -rf .venv`

- [x] **Step 4: Env files** (from the laptop, so passwords never appear in a terminal transcript)
  - **Run:** Build two files in the scratchpad (mode 600) and pipe each over SSH into `sudo install`:
    - `app.env`: `DATABASE_URL='postgresql://career_app:<app pw>@<RDS_HOST>:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5'`, with the value **in single quotes**, because `deploy.sh` loads the file with `.` and an unquoted `&` would end the assignment. The password is percent-encoded.
    - `migrate.env`: the same URL with `career_admin` and the master password.

    On the server: `sudo install -d -m 755 /etc/career-platform`. Install `app.env` with `-o root -g career-app -m 640` and `migrate.env` with `-o ubuntu -g ubuntu -m 600`. Then delete the scratchpad copies.
  - **Check:**
    - `sudo -u career-app cat /etc/career-platform/migrate.env` fails with `Permission denied`.
    - `sudo -u career-app test -r /etc/career-platform/app.env && echo ok` prints `ok`.
    - `(set -a; . /etc/career-platform/migrate.env; psql "$DATABASE_URL" -Atc 'select version(), ssl from pg_stat_ssl where pid = pg_backend_pid()')` prints `PostgreSQL 18.6…|t`, which proves verify-full TLS from EC2.
  - **Undo:** `sudo rm -rf /etc/career-platform`

> **Executed 2026-11-09: complete.**
> - SSH needed a new port 22 rule: the public IP had changed on the same network, so `laptop-2026-11-03` was replaced with `laptop-2026-11-09`.
> - Step 1: `pg_restore` 18.6, Python 3.14.4, uv 0.12.19, nginx 1.28.3, certbot 4.0.0. No reboot was needed.
> - Step 2: the server is on `ceaf1ed`, the pushed branch head. 114 CA certificates.
> - Step 3: 55 passed on Python 3.14.4. The venv points to `/usr/bin/python3.14`, and `career-app` can import `app.main`. `uv run` warns that `.python-version` asks for 3.12; this is harmless, because systemd and `deploy.sh` call `.venv/bin` directly.
> - Step 4: the URL values had to be single-quoted, and the files were written with `install -m … /dev/null` followed by `sudo tee`, piped from the laptop with no scratchpad copy (see the migration notes). The checks show `18.6|t` (verify-full TLS from EC2), `career-app` can't read `migrate.env`, and systemd parses `app.env`.

## 5. Data: Railway → RDS, restored from EC2

- [x] **Step 1: Start the content freeze and take a fresh dump**
  - **Where:** laptop
  - **Run:** Follow the `railway-postgres-backup-method` memory: `railway ssh -s Postgres`, then `pg_dump -Fc`, transferred as base64 between markers, with sha256 compared at both ends. Save it as `backups/railway-postgres-<UTC timestamp>.dump`.
  - **Check:** The two sha256 values match. `/opt/homebrew/opt/postgresql@18/bin/pg_restore --list <dump> | grep -c 'TABLE DATA'` is 8 (seven tables plus `alembic_version`).
  - **Undo:** Read-only on Railway.

- [x] **Step 2: Copy the dump to EC2 and restore it into the empty database**
  - **Run:**
    1. `scp -i ~/.ssh/isba4775_aws <dump> ubuntu@<EIP>:/home/ubuntu/railway.dump`, then `chmod 600 ~/railway.dump` on the server. `sha256sum` must match the laptop's `shasum -a 256`.
    2. On the server: `(set -a; . /etc/career-platform/migrate.env; set +a; pg_restore --no-owner --no-acl --exit-on-error -d "$DATABASE_URL" ~/railway.dump)`
  - **Why:**
    - RDS isn't reachable from the laptop, so the restore runs on the instance (course guide, section 9).
    - The target database is empty and the restore runs **before** any `alembic upgrade`, so Alembic later finds `0002` and does nothing.
    - `--no-owner` is needed because Railway's tables belong to `postgres`, which doesn't exist on RDS.
  - **Check:** `select version_num from alembic_version` is `0002_project_category`.
  - **Undo:** As `career_admin`, `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`, then restore again.

- [x] **Step 3: Create the read-only app role**
  - **Run:** From the laptop, pipe the SQL over SSH into `psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f -` (migrate.env loaded on the server), so the password travels only inside SSH. The SQL is built from `~/.config/career-platform/rds-app-password`:
    ```sql
    CREATE ROLE career_app LOGIN PASSWORD '<app pw>';
    GRANT CONNECT ON DATABASE career_platform TO career_app;
    GRANT USAGE ON SCHEMA public TO career_app;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO career_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE career_admin IN SCHEMA public GRANT SELECT ON TABLES TO career_app;
    ```
  - **Why:** The app never writes, so its role only reads. If the app is compromised, it can't change or delete the data.
  - **Check:** With app.env loaded (`sudo -u career-app` or `sudo cat`): `select count(*) from projects` works, and `delete from tags` fails with `permission denied`.
  - **Undo:** `DROP OWNED BY career_app; DROP ROLE career_app;`

- [x] **Step 4: Prove the data matches Railway, then remove the server copy**
  - **Run:** Run this query on Railway (`railway ssh -s Postgres` → `psql -At`) and on RDS (EC2, migrate.env). Save the outputs as `backups/checksums-railway.txt` and `backups/checksums-rds.txt` on the laptop, then `diff` them:
    ```sql
    SELECT 'profiles', count(*), md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) FROM profiles t
    UNION ALL SELECT 'experiences', count(*), md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) FROM experiences t
    -- same line for education, skills, tags, projects, project_tags, alembic_version
    ORDER BY 1;
    ```
    Then run `shred -u ~/railway.dump` on the server.
  - **Check:**
    - `diff` prints nothing.
    - The row counts match the Railway plan's table (profiles 1, experiences 2, education 2, skills 12, tags 13, projects 13, project_tags 27), or the difference is explained by content edits since then.
    - `ls ~/railway.dump` on the server says no such file.
  - **Undo:** Read-only.

> **Executed 2026-11-09: complete, with a different data source.** The career-platform app is gone from Railway: the site and `tmbs117o.up.railway.app` return `404 Application not found`, and the Railway login only sees `traceability-db`. With the user's approval, the source is **`backups/railway-postgres-20261029T215819Z.dump`** (sha256 `88a08d55…`, 8 `TABLE DATA` entries) instead of a fresh dump. Content edits made after 2026-10-29, if any, aren't in it.
> - Step 1: replaced by the Oct 29 dump. The dump attempts first hit the wrong project and needed a Railway SSH key (see the migration notes).
> - Step 2: the sha256 matched on EC2. RDS had 0 tables beforehand. `pg_restore` exited 0, and `alembic_version` is `0002_project_category`.
> - Step 3: the role was created. `career_app` counts 13 projects, and `delete from tags` gets `permission denied`.
> - Step 4: RDS is compared with **the dump restored into a temporary local Postgres 18**, not with Railway. The query sorts with `COLLATE "C"` and both outputs are put through `LC_ALL=C sort`. `diff` is empty (`backups/checksums-dump.txt` and `backups/checksums-rds.txt`). Counts: profiles 1, experiences 2, education 2, **skills 13** (the plan said 12, but the dump has 13), tags 13, projects 13, project_tags 27. The server's copy was shredded.

## 6. Run the app

- [x] **Step 1: Install the unit and nginx site, then deploy**
  - **Run:**
    ```bash
    sudo cp /opt/career-platform/deploy/aws/career-platform.service /etc/systemd/system/
    sudo systemctl daemon-reload && sudo systemctl enable career-platform
    sudo cp /opt/career-platform/deploy/aws/nginx-career-platform.conf /etc/nginx/sites-available/career-platform
    sudo ln -sf /etc/nginx/sites-available/career-platform /etc/nginx/sites-enabled/career-platform
    sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx
    /opt/career-platform/deploy/aws/deploy.sh
    ```
  - **Check:**
    - `deploy.sh` exits 0 and prints the commit.
    - `alembic upgrade head` reports nothing to do.
    - `sudo ss -ltnpH 'sport = :8000'` shows only `127.0.0.1:8000`.
    - `ps -o user= -C uvicorn` shows only `career-app`.
    - `free -m` leaves headroom on the 1 GiB instance. Record it.
    - `curl -s -H 'Host: aws.elliemcgough.me' http://<EIP>/health` from the laptop is `{"status":"ok"}`.
  - **Undo:** `sudo systemctl disable --now career-platform`, remove the unit and the site link, restore the `default` link, and reload nginx.

> **Executed 2026-11-09: complete.**
> - `nginx -t` passed. `deploy.sh` exited 0 and printed `deployed ceaf1ed: /health ok, /about 200`, and Alembic made no changes.
> - uvicorn listens only on `127.0.0.1:8000` and runs as `career-app`. `free -m` shows 908 MB total and 397 MB available.
> - From the laptop, with `Host: aws.elliemcgough.me`: `/health` returns `{"status":"ok"}`, and `/` returns 307 to `/about`. `/about`, `/contact`, `/portfolio`, `/privacy`, `/resume` and `/projects/1` all return 200 without the snapshot marker, so they're served from RDS.

## 7. Verify on the test subdomain `aws.elliemcgough.me` (course guide, section 10)

Railway keeps serving `elliemcgough.me` throughout this section.

- [x] **Step 1: DNS record for the test name**
  - **Where:** laptop, `cf` CLI
  - **Run:** Add an A record `aws` → `<EIP>`, **DNS only**, TTL Auto. Change no other record.
  - **Check:**
    - `nslookup aws.elliemcgough.me` answers `<EIP>`.
    - `cf dns records list --zone elliemcgough.me` shows every other record unchanged from `docs/evidence/dns-https-final.md`.
    - In the Cloudflare dashboard, the new record has the grey cloud.
  - **Undo:** Delete the `aws` A record.

> **Executed 2026-11-09 (Step 1 only):**
> - Created with `cf dns records create -z elliemcgough.me --body …`: A `aws.elliemcgough.me` → `52.71.186.61`, `proxied: false`, TTL Auto. The record ID is `84c2c106…`, and its comment notes the migration.
> - The zone went from 10 records to 11. A before-and-after diff of all record fields shows nothing removed or changed, and the only addition is this one.
> - The record resolves to the Elastic IP on 1.1.1.1, 8.8.8.8 and Cloudflare's authoritative server. `http://aws.elliemcgough.me/health` returns `{"status":"ok"}`.

- [ ] **Step 2: Certificate for the test name**
  - **Where:** server
  - **Run:**
    1. `sudo certbot certonly --nginx -d aws.elliemcgough.me --dry-run`
    2. If that passes: `sudo certbot --nginx -d aws.elliemcgough.me --redirect --agree-tos --no-eff-email -m <your email>`
  - **Why:** The staging dry run protects you from Let's Encrypt's limit of five failed validations an hour.
  - **Check:**
    - `sudo nginx -t` passes.
    - `git -C /opt/career-platform status --short` is empty.
    - `https://aws.elliemcgough.me` shows the padlock in the browser.
    - `sudo certbot renew --dry-run` succeeds.
  - **Undo:** `sudo certbot delete --cert-name aws.elliemcgough.me`, then copy the plain port-80 config back.

- [ ] **Step 3: Every page matches Railway**
  - **Where:** laptop
  - **Run:** For `/about /resume /portfolio /contact /privacy /no-such-page` plus `/projects/<id>` for every id in `select id from projects`:
    - Fetch the page from `https://elliemcgough.me` (Railway) and from `https://aws.elliemcgough.me` (EC2).
    - Normalize both with `sed -E 's#https://(aws\.)?elliemcgough\.me##g'`, then `diff`.
    - Also record each status code.
  - **Check:**
    - No diffs.
    - The `/no-such-page` page has status 404 and every other page 200 on both sides.
    - The fallback marker count is 0 on every EC2 page.
    - The `og:image` on EC2's `/about` starts with `https://aws.elliemcgough.me/`.
    - `curl -sI http://aws.elliemcgough.me/` gives `301` to HTTPS.
  - **Undo:** Read-only.

- [ ] **Step 4: Database outage gives a fast 503, then recovers** (closes the Project 1 gap "never triggered live")
  - **Run:**
    1. Revoke the `career-platform-db` 5432 rule. Then `sudo systemctl restart career-platform` (existing connections survive a security group change).
    2. Time `curl -s -o /dev/null -w '%{http_code} %{time_total}\n' https://aws.elliemcgough.me/about`.
    3. Re-authorize the rule, wait 10 s, and fetch again **without** restarting.
  - **Check:**
    - During the outage: `503` in under 15 s, with the marker present.
    - After re-authorizing: `200` with the marker absent.
  - **Undo:** Re-authorize the rule (Section 3 Step 2).

- [ ] **Step 5: Record the tests**
  - **Run:** Write `docs/evidence/aws-test-subdomain.md` with what was tested, the commands and output, and what is still unverified.

## 8. Cut the domain over to EC2 (course guide, section 11)

Gate: Section 7 all passed. Not required during class, but it must happen before the Railway trial ends. This changes what the public sees, so **ask the user before Step 2.** Expected outage: from the DNS change until Certbot finishes, usually under 10 minutes.

- [ ] **Step 1: Last data check**
  - **Run:** Rerun Section 5 Step 4's checksum query.
  - **Check:** No diff. If Railway content changed, repeat Section 5 first.

- [ ] **Step 2: Point the apex at the Elastic IP**
  - **Where:** `cf` CLI or the Cloudflare dashboard
  - **Run:** Replace the `elliemcgough.me` CNAME (`tmbs117o.up.railway.app`) with an **A record to `<EIP>`, DNS only**, TTL Auto. **Do not touch** `www`, the redirect rule, `_railway-verify`, `aws`, MX or any TXT records.
  - **Check:** `nslookup elliemcgough.me` and `dig +short elliemcgough.me @8.8.8.8` both print `<EIP>`.
  - **Undo:** Put back the CNAME to `tmbs117o.up.railway.app`, DNS only. Railway is unchanged and still has the custom domain.

- [ ] **Step 3: Add the apex to the certificate**
  - **Where:** server
  - **Run:**
    1. `sudo certbot certonly --nginx --cert-name aws.elliemcgough.me -d aws.elliemcgough.me -d elliemcgough.me --dry-run`
    2. If that passes: the same command without `--dry-run` and with `--expand`, then `sudo certbot install --nginx --cert-name aws.elliemcgough.me`.
  - **Why:**
    - `www` is answered by Cloudflare, so the certificate only needs the apex and the test name.
    - If validation reaches Railway, DNS caches haven't updated yet. Wait 5 minutes and retry.
  - **Check:** `sudo nginx -t` passes. `git -C /opt/career-platform status --short` is empty.
  - **Undo:** Re-issue for `aws.elliemcgough.me` alone.

- [ ] **Step 4: Check the real domain is on EC2**
  - **Where:** laptop
  - **Run and check:**
    - `curl -sI https://elliemcgough.me/about` shows a 200 and `server: nginx`.
    - `curl -sI http://elliemcgough.me/` gives `301` to `https://elliemcgough.me/`.
    - `curl -sI https://www.elliemcgough.me/` gives `301` to `https://elliemcgough.me/` (the Cloudflare rule).
    - `openssl s_client -connect elliemcgough.me:443 -servername elliemcgough.me </dev/null 2>/dev/null | openssl x509 -noout -issuer -ext subjectAltName` shows Let's Encrypt and both names.
    - The `og:image` on `/about` starts with `https://elliemcgough.me/`.
    - The fallback marker count is 0.
    - The padlock shows in the browser.
  - The content freeze ends here. Record everything in `docs/evidence/aws-cutover.md`.
  - **Undo:** Section 8 Step 2's undo. The app doesn't write, but if any content was edited on RDS after cutover, copy it back to Railway before rolling back (course guide, section 11).

## 9. After cutover: merge, document (course guide, sections 11–12)

- [ ] **Step 1: Merge to `main` and run `main` on the server**
  - **Run:** Change `deploy.sh`'s default ref to `origin/main` and commit. Merge `aws-ec2-rds-migration` into `main` and push (ask first). On the server, run `deploy.sh origin/main`. Then delete the branch locally and on GitHub.
  - **Why:** Once the domain points at AWS, Railway no longer serves anything that matters, so its redeploy from `main` is harmless.
  - **Check:** The site still loads at `https://elliemcgough.me` with no fallback marker. `git -C /opt/career-platform rev-parse --short HEAD` matches `origin/main`.

- [ ] **Step 2: README**
  - **Run:** Update the README for the move, with a Mermaid architecture diagram:
    - Cloudflare DNS → nginx (HTTPS ends here) → uvicorn on loopback → RDS in the VPC, with its 1-day backups.
    - SSH as the only admin path.
    - Railway, if it still serves anything.
    - Unfinished items marked.
  - **Check:** The README covers five things:
    - which architecture and why
    - how the database is backed up and restored
    - what was tested on `aws.` and what passed
    - the monthly cost
    - what's next

    No passwords, keys or exports. Every arrow in the diagram matches the deployment.

- **Later (not this plan):**
  - Retire Railway: remove the custom domain and `_railway-verify`, then shut down the service and its database. Do it before the trial ends, and after a few days on AWS.
  - Rewrite `docs/how-this-site-is-secured.md` and `docs/request-path.md` for AWS.
  - Content edits now go to RDS as `career_admin`, from EC2. `scripts/*.sql` are still SQLite-only.

## 10. Costs and teardown

- **Costs** (us-east-1 public price list of 2026-11-03, on-demand, 730 hours):

  | Item | Monthly |
  | --- | --- |
  | `t3.micro` ($0.0104/hr) | $7.59 |
  | `db.t4g.micro` Single-AZ ($0.016/hr) | $11.68 |
  | EC2 gp3, 20 GB ($0.08/GB-month) | $1.60 |
  | RDS gp3, 20 GB ($0.115/GB-month) | $2.30 |
  | Public IPv4, Elastic IP ($0.005/hr) | $3.65 |
  | Backups (within the free amount) | $0.00 |
  | Data out (under 100 GB/month free) | $0.00 |
  | **Total** | **$26.82** |

  - On the Free plan's $100 in credits, that's about 113 days.
  - Stopping the database only pauses it: RDS restarts it after 7 days.
  - Stopping the instance still bills the Elastic IP and the volumes.
- **Teardown at the end of the course:**
  1. Point DNS elsewhere.
  2. `aws rds modify-db-instance --db-instance-identifier career-platform-db --no-deletion-protection --apply-immediately`
  3. `aws rds delete-db-instance --db-instance-identifier career-platform-db --final-db-snapshot-identifier career-platform-db-final`. Snapshots are billed; delete the snapshot too if you don't need it.
  4. `delete-db-subnet-group`
  5. `terminate-instances`
  6. `disassociate-address`, then `release-address`
  7. `delete-security-group` for `sg-0d2918f4b6db4e9a3`, then `sg-0e35c236b5e8b76c1`
  8. `delete-key-pair`
  9. Delete the Cloudflare `aws` record.
  10. Confirm `describe-addresses`, `describe-volumes` and `describe-db-snapshots` are empty or intended.

## Rollback (reverse order)

1. **The domain is broken after cutover:** put the Cloudflare apex back to the CNAME `tmbs117o.up.railway.app` (DNS only). Railway is untouched, so the site returns when DNS updates.
2. **The app is broken on EC2:** `deploy.sh <previous commit>` redeploys a known-good commit. Logs: `journalctl -u career-platform -n 200`.
3. **Remove AWS entirely:** Section 10 teardown.
