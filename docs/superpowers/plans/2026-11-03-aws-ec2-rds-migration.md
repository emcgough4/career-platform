# AWS EC2 and RDS Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. As each section finishes, tick its boxes and add an `> **Executed YYYY-MM-DD: …**` note under it, the same way the earlier plans do.

**Goal:** Serve elliemcgough.me from an EC2 instance in us-east-1, backed by a Single-AZ RDS PostgreSQL 18 database, with Railway kept running unchanged as the rollback.

**Architecture:** The app code stays the same FastAPI + SQLAlchemy app. On one `t3.small` Ubuntu 24.04 instance, nginx terminates HTTPS (Certbot, Let's Encrypt) and proxies to uvicorn on `127.0.0.1:8000`, run by systemd as an unprivileged `career-app` user. The app connects to a private, encrypted `db.t4g.micro` RDS instance over TLS (`verify-full`) as a read-only role. Migrations run as the owner role, only from a deploy script. The data moves once, with a `pg_dump` from Railway restored from the laptop through an SSH tunnel via EC2. Then Cloudflare's apex record moves from Railway to the instance's Elastic IP.

**Tech Stack:** AWS CLI v2 (profile `isba-4775`), EC2, Elastic IP, RDS for PostgreSQL 18.6, Ubuntu 24.04, nginx, Certbot, systemd, uv 0.12.19, Python 3.12, FastAPI, uvicorn, SQLAlchemy 2.1, Alembic, psycopg 3, Homebrew `postgresql@18` (laptop), Railway CLI, Cloudflare DNS.

**Spec:** The request in chat on 2026-11-03: "Look at my app and help me plan its move to AWS. Use EC2 for the app and a Single-AZ RDS PostgreSQL database. Work on a new branch so Railway doesn't redeploy from main. Don't create anything yet." Decisions from the interview that day: the domain moves to AWS; the account is the user's alone; the cutover allows a few minutes of downtime (Certbot HTTP challenge after the DNS flip). The constraints come from the course policy `LMU-ISBA/isba-4775-fa26/guides/aws-ec2-deployment-policy.json`.

## What's there today (found 2026-11-03, read-only)

| Item | Value |
| --- | --- |
| Live site | `https://elliemcgough.me`, `server: railway-hikari`. Apex is a DNS-only CNAME to `tmbs117o.up.railway.app`. `www` is a proxied placeholder (`192.0.2.1`) that a Cloudflare rule 301s to the apex (`docs/evidence/dns-https-final.md`). MX/SPF/DKIM/DMARC/Zoho TXT records are for mail and must not change. |
| Railway DB | PostgreSQL 18.6, private network only. Backup method: `railway ssh -s Postgres` → `pg_dump -Fc` (memory `railway-postgres-backup-method`). Last dump: `backups/railway-postgres-20261029T215819Z.dump` |
| App | 6 GET routes plus `/health` (no DB). **No write paths**: no POST/PUT/DELETE, no `commit()`. On a DB error the pages return **503** with the snapshot and the marker `<!-- Showing the latest saved profile snapshot. -->` |
| Config | `DATABASE_URL` → `app/config.py` (`postgres(ql)://` rewritten to `postgresql+psycopg://`). `alembic/env.py` passes it to `config.set_main_option`, which is a configparser call, so a `%` in the URL (URL-encoded password) raises `ValueError` |
| Railway-only pieces | `railway.json` (preDeploy `alembic upgrade head`, `--forwarded-allow-ips=*`, `/health` check, restart policy), `railpack.json`, `tests/test_railway_config.py`. **They stay as they are** so Railway keeps working as the rollback |
| AWS account `909096719723` | Empty: default VPC `vpc-02ed278a349b93372` (`172.31.0.0/16`), six default public subnets (us-east-1a `subnet-091fafd64394acaf2`, b `subnet-0dbd1bce00600192f`, c `subnet-0b1960fc8f1fe3b0d`, d `subnet-0c624206cd7096d5f`, e `subnet-088369ecdfbb283bb`, f `subnet-006a7c5373439e854`). No instances, DBs, key pairs or EIPs, and only the `default` SG. RDS offers postgres 18.1 to 18.6 |
| Laptop | `uv 0.12.19`, Homebrew `postgresql@18 18.6_1` (keg-only: `/opt/homebrew/opt/postgresql@18/bin`), `~/.ssh/isba4775_azure` (Azure key, not reused). `env/` and `backups/` are git-ignored |
| Repo | `https://github.com/emcgough4/career-platform`, public |

## Policy rules this plan must satisfy

From the course policy. Each one is handled by a flag in Section 3:

- Region `us-east-1` only. EC2 `t3.micro`/`t3.small` only. `HttpTokens=required` at launch.
- RDS `db.t3.micro`/`db.t4g.micro`, not Multi-AZ, ≤ 20 GB, encrypted, never publicly accessible. **Pass `--storage-encrypted` and `--no-publicly-accessible` explicitly**: the policy's Denies use `BoolIfExists`, so leaving the flags out can be denied.
- Not allowed: VPC changes, `ModifyInstanceAttribute` (no resizing, no swapping security groups on a running instance), `CreateKeyPair` (import only), `iam:PassRole` (no instance role, so no Secrets Manager, SSM Session Manager or CloudWatch agent), and Secrets Manager–managed RDS passwords.

## Global Constraints

- Every AWS command runs with `export AWS_PROFILE=isba-4775 AWS_REGION=us-east-1` set first. (zsh doesn't word-split `$VAR`, so don't put flags in a variable.)
- Names: key pair `isba4775-aws`, SGs `career-platform-web` and `career-platform-db`, instance `Name=career-platform`, EIP `Name=career-platform`, DB subnet group and DB instance `career-platform-db`, database `career_platform`, RDS owner `career_admin`, app role `career_app`.
- AZ `us-east-1a` for both the instance and the database (no cross-AZ traffic).
- Values found at run time are written into the Executed notes as `<AMI_ID>`, `<INSTANCE_ID>`, `<WEB_SG>`, `<DB_SG>`, `<EIP>`, `<EIP_ALLOC>`, `<RDS_HOST>`, `<HOME_IP>`, `<SCHOOL_IP>`. IDs and the public IP may be recorded. **Passwords, full `DATABASE_URL`s and dumps never go into the repo, the plan or chat.**
- Passwords: `openssl rand -hex 24` (hex only, so nothing needs URL-encoding). Stored on the laptop in `~/.config/career-platform/rds-master-password` and `~/.config/career-platform/rds-app-password`, mode 600.
- Server layout: code in `/opt/career-platform` (owner `ubuntu`). App env `/etc/career-platform/app.env` (`root:career-app`, 0640). Migration env `/etc/career-platform/migrate.env` (`ubuntu:ubuntu`, 0600). RDS CA `/etc/ssl/certs/rds-global-bundle.pem`.
- App `DATABASE_URL` query string: `?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5`.
- Python comes from Ubuntu's `/usr/bin/python3.12` (`UV_PYTHON_PREFERENCE=only-system`), never a uv-managed Python under `~ubuntu`, because `career-app` can't read `/home/ubuntu`.
- Code work happens on branch `aws-ec2-rds-migration`. **Never push to `main`, and don't open a PR** (a PR can trigger a Railway preview deploy). Ask before the one `git push -u origin aws-ec2-rds-migration` in Section 2.
- Railway's service, variables, custom domain and `railway.json` are not changed by this plan.
- **Content freeze** from Section 5 Step 1 until Section 7 is done. No edits to Railway's database in that time.
- Local tests keep using SQLite. No test needs AWS or Postgres.

## Review Focus

- **`%` in a database URL crashes Alembic.** `set_main_option` is configparser, and `%40` reads as interpolation. Task 2 escapes it and tests offline migration with an encoded password.
- **uvicorn trusting every forwarded header.** Railway needs `--forwarded-allow-ips=*`; on EC2 it lets anyone fake `X-Forwarded-Proto` and the client IP. Task 1 tests that the unit binds `127.0.0.1` and doesn't pass that flag. Section 7 checks `og:image` is `https://`.
- **A DB outage that hangs instead of falling back.** With no `connect_timeout`, a blocked RDS connection waits about 2 minutes per request. Task 2 pins the URL query. Section 6 Step 4 blocks the DB and expects a 503 with the marker within a few seconds, then recovery once it's unblocked.
- **The app user can't read the Python.** If uv downloads its own Python into `~ubuntu/.local`, `career-app` gets "permission denied" at start. Task 1's deploy script sets `UV_PYTHON_PREFERENCE=only-system`. Section 4 Step 3 checks `readlink -f .venv/bin/python` is `/usr/bin/python3.12`.
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
- Produces: `deploy/aws/deploy.sh [git-ref]`, run on the server as `ubuntu` from any directory. It exits 0 only if `/health` returns `{"status":"ok"}` and `/about` returns 200 (not 503) after the restart. Sections 4 and 6 call it.

- [ ] **Step 1: Write the failing tests** in `tests/test_aws_deploy_config.py`. They read the three files as text from `REPO_ROOT / "deploy" / "aws"`:

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

def test_nginx_proxies_to_loopback_for_the_apex():
    conf = read("nginx-career-platform.conf")
    assert "listen 80 default_server;" in conf
    assert "server_name elliemcgough.me;" in conf
    assert "proxy_pass http://127.0.0.1:8000;" in conf
    for header in ["Host $host", "X-Forwarded-For $proxy_add_x_forwarded_for", "X-Forwarded-Proto $scheme"]:
        assert f"proxy_set_header {header};" in conf

def test_deploy_script_syncs_then_migrates_as_owner_then_restarts_then_checks():
    script = read("deploy.sh")
    assert script.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    steps = ["UV_PYTHON_PREFERENCE=only-system", "uv sync --locked", "/etc/career-platform/migrate.env",
             "alembic upgrade head", "systemctl restart career-platform", "/health", "/about"]
    positions = [script.index(step) for step in steps]
    assert positions == sorted(positions)

def test_deploy_script_is_executable():
    assert os.access(DEPLOY / "deploy.sh", os.X_OK)
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_aws_deploy_config.py -v`
Expected: 5 FAIL with `FileNotFoundError` (no `deploy/aws/`).

- [ ] **Step 3: Write the three files**
  - `career-platform.service`: the Azure unit from `2026-10-01-operate-the-vm.md` Task 2, with the user, paths and env file above, `After=network-online.target` and `Wants=network-online.target`, and `RestartSec=3`.
  - `nginx-career-platform.conf`: one `server` block on port 80 (`listen 80 default_server;` and `listen [::]:80 default_server;`, `server_name elliemcgough.me;`), with `location /` proxying as in the tests. Certbot adds the 443 block in Section 7. `default_server` lets Section 6 test by IP before DNS moves.
  - `deploy.sh`:
    1. `cd /opt/career-platform`, then `git fetch origin` and `git checkout --detach "${1:-origin/aws-ec2-rds-migration}"`.
    2. `UV_PYTHON_PREFERENCE=only-system uv sync --locked`.
    3. In a subshell: `set -a; . /etc/career-platform/migrate.env; set +a; .venv/bin/alembic upgrade head`.
    4. `sudo systemctl restart career-platform`.
    5. Poll `curl -fsS http://127.0.0.1:8000/health` up to 15 times, one second apart.
    6. Require `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/about` to be `200`. Print a one-line summary with the deployed commit (`git rev-parse --short HEAD`).

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest -q`
Expected: all pass (the existing 48 plus 5 new).

- [ ] **Step 5: Commit**

```bash
git add deploy/aws tests/test_aws_deploy_config.py
git commit -m "feat: add the systemd unit, nginx site and deploy script for EC2"
```

## 2. Code: database URL safety (Task 2)

### Task 2: Alembic accepts `%` in the URL; the RDS query string survives

**Files:**
- Modify: `alembic/env.py` (the `set_main_option` line)
- Modify: `.env.example` (comment showing the RDS URL shape with placeholders)
- Test: `tests/test_alembic_env.py`, `tests/test_config.py`

**Interfaces:**
- Consumes: `normalize_database_url(url: str) -> str` (unchanged).
- Produces: nothing new. `alembic upgrade head` works for any valid URL.

- [ ] **Step 1: Write the failing test** in `tests/test_alembic_env.py`. Use the subprocess pattern from `tests/test_config.py`:

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

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_alembic_env.py -v`
Expected: FAIL, with stderr containing `invalid interpolation syntax`.

- [ ] **Step 3: Escape `%` as `%%`** in `alembic/env.py`: `config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))`, plus a one-line comment saying why. Add the `.env.example` comment:
  `# AWS (EC2 → RDS): postgresql://career_app:<password>@<rds-host>:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5`

- [ ] **Step 4: Run the tests to see them pass**

Run: `uv run pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit, then push the branch (ask first)**

```bash
git add alembic/env.py .env.example tests/test_alembic_env.py tests/test_config.py
git commit -m "fix: let Alembic accept percent-encoded database URLs"
git push -u origin aws-ec2-rds-migration   # only after the user says yes
```
Check: `git log origin/main..origin/aws-ec2-rds-migration --oneline` lists this plan's commits, and `origin/main` has not moved. Railway shows no new deployment.

## 3. AWS resources (laptop, AWS CLI)

Gate: Sections 1–2 done. **Everything from here on is billed.** Ask the user before Step 3. Each step's Undo is listed again in reverse order under Rollback.

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

> **Executed 2026-11-03: passwords only; the SSH key is not done yet.**
> - The passwords live in `~/.config/career-platform/` (directory 700, files 600, 48 hex characters each), outside the repository as the course guide asks, instead of the git-ignored `env/`. They were never printed.
> - The SSH key is generated and imported with Section 3 Step 3.

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

- [ ] **Step 3: Launch the instance (dry run first)**
  - **Run:**
    ```bash
    AMI_ID=$(aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id --query Parameter.Value --output text)
    aws ec2 run-instances --dry-run --image-id "$AMI_ID" --instance-type t3.small --key-name isba4775-aws \
      --subnet-id subnet-091fafd64394acaf2 --security-group-ids <WEB_SG> \
      --metadata-options HttpTokens=required,HttpEndpoint=enabled,HttpPutResponseHopLimit=1 \
      --credit-specification CpuCredits=standard \
      --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=10,VolumeType=gp3,Encrypted=true,DeleteOnTermination=true}' \
      --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=career-platform}]' 'ResourceType=volume,Tags=[{Key=Name,Value=career-platform-root}]'
    ```
    The dry run should print `DryRunOperation`. Then rerun the same command without `--dry-run`, adding `--query 'Instances[0].InstanceId' --output text`, and then run `aws ec2 wait instance-status-ok --instance-ids <INSTANCE_ID>`.
  - **Why:**
    - `t3.small` gives 2 GiB of RAM; the type can't be changed later under the policy.
    - `CpuCredits=standard` avoids unlimited-credit charges.
    - The encrypted 10 GB root volume leaves room for the venv and logs.
  - **Check:** `describe-instances` shows `t3.small`, `running`, `MetadataOptions.HttpTokens: required`, AZ `us-east-1a`. `describe-instance-credit-specifications` shows `standard`. If `Encrypted=true` is denied (KMS), record it and rerun with `Encrypted=false`.
  - **Undo:** `aws ec2 terminate-instances --instance-ids <INSTANCE_ID>`

- [ ] **Step 4: Elastic IP**
  - **Run:** `allocate-address --domain vpc --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=career-platform}]'`, then `associate-address --instance-id <INSTANCE_ID> --allocation-id <EIP_ALLOC>`.
  - **Why:** The address survives stop and start, so the Cloudflare A record keeps working.
  - **Check:** `ssh -i ~/.ssh/isba4775_aws ubuntu@<EIP> 'lsb_release -ds; curl -s -o /dev/null -w "%{http_code}\n" http://169.254.169.254/latest/meta-data/'` prints `Ubuntu 24.04…`, then `401` (IMDSv1 refused).
  - **Undo:** `disassociate-address --association-id …`, then `release-address --allocation-id <EIP_ALLOC>`.

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
  - **Undo:** Section 9 (teardown). Deletion protection must be turned off first.

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
> - **Not waited on**, as the course guide suggests. `<RDS_HOST>` and the `available` check get recorded when it finishes.

## 4. Server setup (SSH as `ubuntu`)

- [ ] **Step 1: Packages, app user, uv**
  - **Run:**
    ```bash
    sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get install -y git nginx certbot python3-certbot-nginx
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin career-app
    curl -LsSf https://astral.sh/uv/0.12.19/install.sh | sh && source ~/.local/bin/env
    [ -f /var/run/reboot-required ] && sudo reboot
    ```
  - **Check:** `uv --version` prints `uv 0.12.19`, `id career-app` works, `nginx -v` and `certbot --version` print versions.
  - **Undo:** `sudo userdel career-app`. The packages can stay.

- [ ] **Step 2: Clone the branch and fetch the RDS CA bundle**
  - **Run:**
    ```bash
    sudo install -d -o ubuntu -g ubuntu -m 755 /opt/career-platform
    git clone --branch aws-ec2-rds-migration https://github.com/emcgough4/career-platform.git /opt/career-platform
    sudo curl -fsSL -o /etc/ssl/certs/rds-global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
    ```
  - **Check:** `git -C /opt/career-platform log -1 --oneline` matches the laptop's branch head. `grep -c 'BEGIN CERTIFICATE' /etc/ssl/certs/rds-global-bundle.pem` is > 1.
  - **Undo:** `sudo rm -rf /opt/career-platform /etc/ssl/certs/rds-global-bundle.pem`

- [ ] **Step 3: Python environment from the lock file and the system Python**
  - **Run:** `cd /opt/career-platform && UV_PYTHON_PREFERENCE=only-system uv sync --locked && uv run pytest -q`
  - **Check:** `readlink -f .venv/bin/python` is `/usr/bin/python3.12`. All tests pass (they use SQLite). `sudo -u career-app /opt/career-platform/.venv/bin/python -c 'import app.main'` exits 0.
  - **Undo:** `rm -rf .venv`

## 5. Data: Railway → RDS

- [ ] **Step 1: Start the content freeze and take a fresh dump**
  - **Where:** laptop
  - **Run:** Follow the `railway-postgres-backup-method` memory: `railway ssh -s Postgres`, then `pg_dump -Fc`, transferred as base64 between markers, with sha256 compared at both ends. Save it as `backups/railway-postgres-<UTC timestamp>.dump`.
  - **Check:** The two sha256 values match. `/opt/homebrew/opt/postgresql@18/bin/pg_restore --list <dump> | grep -c 'TABLE DATA'` is 8 (seven tables plus `alembic_version`).
  - **Undo:** Read-only on Railway.

- [ ] **Step 2: Open a tunnel to RDS through EC2**
  - **Where:** laptop, in a second terminal
  - **Run:** `ssh -i ~/.ssh/isba4775_aws -N -L 15432:<RDS_HOST>:5432 ubuntu@<EIP>`
  - **Why:** RDS isn't public. Port 15432 avoids your local test Postgres on 5433. Use `sslmode=require` through the tunnel, because `verify-full` checks the hostname and the tunnel's hostname is `127.0.0.1`.
  - **Check:** `PGPASSWORD=$(cat ~/.config/career-platform/rds-master-password) /opt/homebrew/opt/postgresql@18/bin/psql "host=127.0.0.1 port=15432 user=career_admin dbname=career_platform sslmode=require" -Atc 'select version(), ssl from pg_stat_ssl where pid = pg_backend_pid()'` prints `PostgreSQL 18.6…|t`.
  - **Undo:** Ctrl-C the tunnel.

- [ ] **Step 3: Restore, then create the read-only app role**
  - **Where:** laptop, with the tunnel open
  - **Run:**
    1. `pg_restore --no-owner --no-acl --exit-on-error -h 127.0.0.1 -p 15432 -U career_admin -d career_platform <dump>`, with `PGSSLMODE=require` and `PGPASSWORD` set from the file.
    2. In `psql` with `-v app_pw="$(cat ~/.config/career-platform/rds-app-password)"`, run:

    ```sql
    CREATE ROLE career_app LOGIN PASSWORD :'app_pw';
    GRANT CONNECT ON DATABASE career_platform TO career_app;
    GRANT USAGE ON SCHEMA public TO career_app;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO career_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE career_admin IN SCHEMA public GRANT SELECT ON TABLES TO career_app;
    ```
  - **Why:**
    - `--no-owner` is needed because Railway's tables belong to `postgres`, which doesn't exist on RDS.
    - The app never writes, so its role only reads. If the app is compromised, it can't change or delete the data.
  - **Check:** `select version_num from alembic_version` is `0002_project_category`. As `career_app`, `select count(*) from projects` works and `delete from tags` fails with `permission denied`.
  - **Undo:** `DROP OWNED BY career_app; DROP ROLE career_app;`, then drop and recreate the `public` schema as `career_admin`, and restore again.

- [ ] **Step 4: Prove the data matches Railway**
  - **Where:** laptop
  - **Run:** Run this query on Railway (`railway ssh -s Postgres` → `psql -At`) and on RDS (tunnel). Save the outputs as `backups/checksums-railway.txt` and `backups/checksums-rds.txt`, then `diff` them:
    ```sql
    SELECT 'profiles', count(*), md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) FROM profiles t
    UNION ALL SELECT 'experiences', count(*), md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) FROM experiences t
    -- same line for education, skills, tags, projects, project_tags, alembic_version
    ORDER BY 1;
    ```
  - **Check:** `diff` prints nothing, and the row counts match the Railway plan's table (profiles 1, experiences 2, education 2, skills 12, tags 13, projects 13, project_tags 27) or are explained by content edits since then.
  - **Undo:** Read-only.

## 6. Run the app and verify by IP (before DNS)

- [ ] **Step 1: Write the env files** (from the laptop, so passwords never appear in a terminal transcript)
  - **Run:** Build two files locally in `env/` (mode 600) and pipe each over SSH into `sudo install`:
    - `env/aws-app.env`: `DATABASE_URL=postgresql://career_app:<app pw>@<RDS_HOST>:5432/career_platform?sslmode=verify-full&sslrootcert=/etc/ssl/certs/rds-global-bundle.pem&connect_timeout=5`
    - `env/aws-migrate.env`: the same URL with `career_admin` and the master password.

    On the server: `sudo install -d -m 755 /etc/career-platform`. Install `app.env` with `-o root -g career-app -m 640` and `migrate.env` with `-o ubuntu -g ubuntu -m 600`.
  - **Check:** `sudo -u career-app cat /etc/career-platform/migrate.env` fails with `Permission denied`, and `sudo -u career-app test -r /etc/career-platform/app.env && echo ok` prints `ok`.
  - **Undo:** `sudo rm -rf /etc/career-platform`

- [ ] **Step 2: Install the unit and nginx site, then deploy**
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
    - `alembic upgrade head` reports nothing to do, because the restore already brought the schema to `0002`.
    - `sudo ss -ltnpH 'sport = :8000'` shows only `127.0.0.1:8000`.
    - `ps -o user= -C uvicorn` shows only `career-app`.
  - **Undo:** `sudo systemctl disable --now career-platform`, remove the unit and the site link, restore the `default` link, and reload nginx.

- [ ] **Step 3: Every page matches Railway**
  - **Where:** laptop
  - **Run:** For `/about /resume /portfolio /contact /privacy /no-such-page` plus `/projects/<id>` for every id in `select id from projects`:
    - Fetch the page from `https://elliemcgough.me` (Railway) and from `http://<EIP>` with `-H 'Host: elliemcgough.me'` (EC2).
    - Normalize both with `sed -E 's#https?://elliemcgough\.me##g'`, then `diff`.
    - Also record each status code.
  - **Check:**
    - No diffs.
    - The `/no-such-page` page has status 404 and every other page 200 on both sides.
    - `grep -c 'Showing the latest saved profile snapshot'` is 0 on every EC2 page.
    - `curl -s http://<EIP>/health` is `{"status":"ok"}`.
  - **Undo:** Read-only.

- [ ] **Step 4: Database outage gives a fast 503, then recovers** (closes the Project 1 gap "never triggered live")
  - **Run:**
    1. Revoke the `career-platform-db` 5432 rule. Then `sudo systemctl restart career-platform` (existing connections survive a security group change).
    2. Time `curl -s -o /dev/null -w '%{http_code} %{time_total}\n' http://<EIP>/about`.
    3. Re-authorize the rule, wait 10 s, and fetch again **without** restarting.
  - **Check:**
    - During the outage: `503` in under 15 s, with the marker present.
    - After re-authorizing: `200` with the marker absent.
    - Record both in a new `docs/evidence/aws-db-outage.md`.
  - **Undo:** Re-authorize the rule (Section 3 Step 2).

## 7. Cut the domain over to EC2

Gate: Sections 5 and 6 all passed. This changes what the public sees, so **ask the user before Step 2.** Expected outage: from the DNS change until Certbot finishes, usually under 10 minutes.

- [ ] **Step 1: Last data check**
  - **Run:** Rerun Section 5 Step 4.
  - **Check:** No diff. If Railway content changed, repeat Section 5 Steps 1, 3 and 4 first.

- [ ] **Step 2: Point the apex at the Elastic IP**
  - **Where:** Cloudflare dashboard, or `cf` CLI (done by the user)
  - **Run:** Replace the `elliemcgough.me` CNAME (`tmbs117o.up.railway.app`) with an **A record to `<EIP>`, DNS only**, TTL Auto. **Do not touch** `www`, the redirect rule, `_railway-verify`, MX or any TXT records.
  - **Check:** `dig +short elliemcgough.me @8.8.8.8` and `@1.1.1.1` both print `<EIP>`.
  - **Undo:** Put back the CNAME to `tmbs117o.up.railway.app`, DNS only. Railway is unchanged and still has the custom domain.

- [ ] **Step 3: Certificate, staging first**
  - **Where:** server
  - **Run:**
    1. `sudo certbot certonly --nginx -d elliemcgough.me --dry-run`
    2. If that passes: `sudo certbot --nginx -d elliemcgough.me --redirect --agree-tos --no-eff-email -m <your email>`
  - **Why:**
    - The staging dry run protects you from Let's Encrypt's limit of five failed validations an hour.
    - `www` is answered by Cloudflare, so the certificate only needs the apex.
    - If validation reaches Railway, DNS caches haven't updated yet. Wait 5 minutes and retry.
  - **Check:** `sudo nginx -t` passes. `git -C /opt/career-platform status --short` is empty (Certbot edited only `/etc/nginx`).
  - **Undo:** `sudo certbot delete --cert-name elliemcgough.me`, then copy the plain port-80 config back.

- [ ] **Step 4: Check the real domain is on EC2**
  - **Where:** laptop
  - **Run and check:**
    - `curl -sI https://elliemcgough.me/about` shows `HTTP/2 200` or `HTTP/1.1 200`, and `server: nginx`.
    - `curl -sI http://elliemcgough.me/` gives `301` to `https://elliemcgough.me/`.
    - `curl -sI https://www.elliemcgough.me/` gives `301` to `https://elliemcgough.me/` (the Cloudflare rule).
    - `openssl s_client -connect elliemcgough.me:443 -servername elliemcgough.me </dev/null 2>/dev/null | openssl x509 -noout -issuer -enddate` shows a Let's Encrypt issuer.
    - The `og:image` on `/about` starts with `https://elliemcgough.me/`.
    - The fallback marker count is 0.
    - On the server, `sudo certbot renew --dry-run` succeeds and `systemctl list-timers | grep certbot` shows the timer.
  - The content freeze ends here. Record everything in `docs/evidence/aws-cutover.md`.
  - **Undo:** Section 7 Step 2's undo.

## 8. Rollback (reverse order)

1. **The site is broken after cutover:** put the Cloudflare apex back to the CNAME `tmbs117o.up.railway.app` (DNS only). Railway is untouched, so the site returns when DNS updates.
2. **The app is broken on EC2:** `deploy.sh <previous commit>` redeploys a known-good commit. Logs: `journalctl -u career-platform -n 200`.
3. **Remove AWS entirely:** Section 9.

## 9. After cutover (not done by this plan)

- **Keep Railway running for at least a week** as the rollback. Retiring it (removing the custom domain and `_railway-verify`, then shutting down the service and its database) is a separate plan.
- **Docs to rewrite** once the cutover holds: `docs/how-this-site-is-secured.md` (AWS security groups instead of the Azure NSG, the EIP, RDS TLS and the read-only role), the README architecture and decisions, and `docs/request-path.md`.
- **Content edits** now go to RDS as `career_admin` through the Section 5 Step 2 tunnel. `scripts/*.sql` are still SQLite-only.
- **Merging to `main`** redeploys Railway with the extra files, which is harmless. Decide this after Railway is retired.
- **Costs** (approximate on-demand, running all month):

  | Item | Monthly |
  | --- | --- |
  | `t3.small` | about $15 |
  | `db.t4g.micro` | about $12 |
  | RDS gp3, 20 GB | about $2.30 |
  | EC2 root volume, 10 GB | about $0.80 |
  | Public IPv4 (EIP) | about $3.65 |
  | **Total** | **about $34** |

  - Stopping the database only pauses it: RDS restarts it after 7 days.
  - Stopping the instance still bills the EIP and the volumes.
- **Teardown at the end of the course:**
  1. Point DNS elsewhere.
  2. `aws rds modify-db-instance --db-instance-identifier career-platform-db --no-deletion-protection --apply-immediately`
  3. `aws rds delete-db-instance --db-instance-identifier career-platform-db --final-db-snapshot-identifier career-platform-db-final`. Snapshots are billed; delete the snapshot too if you don't need it.
  4. `delete-db-subnet-group`
  5. `terminate-instances`
  6. `disassociate-address`, then `release-address`
  7. `delete-security-group` for `<DB_SG>`, then `<WEB_SG>`
  8. `delete-key-pair`
  9. Confirm `describe-addresses`, `describe-volumes` and `describe-db-snapshots` are empty or intended.
