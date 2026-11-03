# AWS migration notes

Deviations from the plan in [`docs/superpowers/plans/2026-11-03-aws-ec2-rds-migration.md`](superpowers/plans/2026-11-03-aws-ec2-rds-migration.md) and from the course guide (`LMU-ISBA/isba-4775-fa26/guides/aws-migration.md`), newest last. No passwords, connection strings or IP addresses of my networks go in this file.

## 2026-11-03

- **The plan now follows the course guide.** The first draft used a `t3.small` with Ubuntu 24.04, a 10 GB root disk, a restore from the laptop through an SSH tunnel, and verification by IP. I switched to the guide's choices:
  - a `t3.micro` with Ubuntu 26.04 and a 20 GB root disk
  - the restore run from the EC2 instance, with 26.04's Postgres 18 client
  - testing on `aws.elliemcgough.me` before cutover
  - merging to `main` after cutover
- **The database passwords live outside the repository**, in `~/.config/career-platform/` (mode 600), as the guide asks. The first draft had put them in the git-ignored `env/` folder.
- **Order:** the security groups and the RDS database were created before the code tasks (plan Sections 1–2), following guide section 7.
- **RDS backups are kept for 1 day, not 7.** The Free plan rejected 7 through 2 days with `FreeTierRestrictionError: The specified backup retention period exceeds the maximum available to free tier customers`. Only upgrading the account plan removes the limit, and the guide says not to upgrade. Point-in-time restore therefore reaches back only 1 day. Railway and the local dumps in `backups/` stay as longer-term copies.
- **The server's uv uses Ubuntu's system Python** (`UV_PYTHON=/usr/bin/python3`), not the `3.12` in `.python-version`. Ubuntu 26.04 may not ship 3.12, and `.python-version` stays as it is because Railway reads it. `uv.lock` has wheels for 3.12 to 3.14.
- **Confirmed at launch:** the instance's system Python is **3.14.4**. The app hasn't been run on 3.14 yet; Section 4 Step 3 runs the test suite there.
