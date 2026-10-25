# Project 1 submission: Own Your Corner of the Internet

| | |
| --- | --- |
| Repository | https://github.com/emcgough4/career-platform |
| Live site | https://elliemcgough.me |
| Final commit | This commit. The next commit writes its SHA here. |

Items marked **Not yet recorded** are open. `TASKS.md` lists what closes each one.

The only commit after the final commit writes its SHA into this file. It changes nothing else.

**Note:** not every gap could be closed. The Azure VM is shut off, and Railway had problems on 2026-10-21. Section 9 lists what I could and couldn't verify.

## 1. README, original spec and plans

- [README](../README.md)
- Original spec: [2026-09-15 personal resume portfolio design](superpowers/specs/2026-09-15-personal-resume-portfolio-design.md)
- Implementation plan: [2026-09-15 personal resume portfolio plan](superpowers/plans/2026-09-15-personal-resume-portfolio-plan.md)
- Azure plans: [2026-09-24 Azure VM migration](superpowers/plans/2026-09-24-azure-vm-migration.md), [2026-10-01 operate the VM](superpowers/plans/2026-10-01-operate-the-vm.md)
- Railway plan: [2026-10-08 Railway and PostgreSQL migration](superpowers/plans/2026-10-08-railway-postgres-migration.md)
- Railway spec: no separate spec file was written. The plan's "Spec" line quotes the request from 2026-10-08, and the README says so.

## 2. Architecture diagrams

- Request path for Railway and Azure, with Railway also shown in sequence: [request-path.md](request-path.md). Written 2026-10-20 as a study diagram. Home network details are placeholders.
- Architecture diagrams for Railway (with the email and analytics paths) and Azure, with locations, protocols, ports and data flow: [README "Architecture"](../README.md#architecture)

## 3. Migration: plan, data comparison, cutover, rollback

- Plan, written before the change: [Railway plan](superpowers/plans/2026-10-08-railway-postgres-migration.md), commit [`5219f59`](https://github.com/emcgough4/career-platform/commit/5219f59)
- PostgreSQL compatibility changes:
  - psycopg 3 driver: [`fb32663`](https://github.com/emcgough4/career-platform/commit/fb32663)
  - fixed tag order: [`0e85bd2`](https://github.com/emcgough4/career-platform/commit/0e85bd2)
  - copy script: [`2351f5f`](https://github.com/emcgough4/career-platform/commit/2351f5f)
  - Railway config: [`c85db31`](https://github.com/emcgough4/career-platform/commit/c85db31), [`41128da`](https://github.com/emcgough4/career-platform/commit/41128da), [`5488a44`](https://github.com/emcgough4/career-platform/commit/5488a44)
- Source/target data comparison: Railway plan Section 6, executed note of 2026-10-08. Row counts and SHA-256 row checksums for every table matched the live VM database.
- Rendered page comparison: Railway plan Section 5, executed note of 2026-10-08. All 17 pages were byte-identical on Railway and the VM.
- Real change to the original data: **Missing, can't be rerun.** The README's "How current data was preserved" section explains why.
- Cutover timeline (out of order, with up to about 75 minutes of Railway 404) and post-cutover checks: plan Sections 4, 7 and 8 notes, recorded afterward on 2026-10-21. Summary in the [README "Migration from Azure to Railway"](../README.md#migration-from-azure-to-railway) section.
- What Git moved and what needed another method, compatibility changes, and who manages what on Azure vs Railway: [README](../README.md#migration-from-azure-to-railway)
- Rollback for code, schema, data, and the cutover-era VM path: [README "Rollback"](../README.md#rollback)

## 4. Azure HTTP and restart; final DNS and HTTPS

- Azure VM, network rules and SSH: [ex03.md](evidence/ex03.md), and the [operate-the-VM plan](superpowers/plans/2026-10-01-operate-the-vm.md) "VM details"
- Nginx → uvicorn (2 workers, systemd) → SQLite, with port 80 reachable and 8000 closed from the internet: operate-the-VM plan, Tasks 2–5, executed 2026-10-01
- HTTPS on Azure (certificate, renewal dry run, open ports): [how-this-site-is-secured.md](how-this-site-is-secured.md) (Exercise 04)
- Controlled VM restart: **Not yet recorded.**
- DNS zone before Zoho (apex CNAME to Railway, DNS only): [dns-before-zoho.md](evidence/dns-before-zoho.md), captured 2026-10-13
- Final DNS records with their purposes, the `www` redirect rule, the redirect checks, and both certificates with how they renew: [dns-https-final.md](evidence/dns-https-final.md), captured 2026-10-21

## 5. Reviewed change through Railway

- Commit, Railway deployment and live result: [railway-deploy.md](evidence/railway-deploy.md). [`839b0c0`](https://github.com/emcgough4/career-platform/commit/839b0c0) → deployment `3ddcbf11` → GA4 tag live, checked 2026-10-22
- Recovery explanation: [README "Rollback"](../README.md#rollback)
- 503 database-failure page and refreshed snapshot: live since 2026-10-24 in deployment `8d5efc20`, which came from `railway up` rather than GitHub. The running files match [`4f9fdc8`](https://github.com/emcgough4/career-platform/commit/4f9fdc8): [railway-deploy.md](evidence/railway-deploy.md) "Update, 2026-10-25"

## 6. Zoho email

- Receive, reply, new outgoing message, and SPF/DKIM/DMARC results: [ex06.md](evidence/ex06.md) §1–2, commit [`41ade8a`](https://github.com/emcgough4/career-platform/commit/41ade8a)
- Header analysis (which check passed for which domain, and alignment): [zoho-header-check.md](evidence/zoho-header-check.md)
- Message sent before any MX record existed (it never arrived): [ex06.md](evidence/ex06.md) §1, "Before MX" row
- Final MX, SPF, DKIM and DMARC records, checked against 8.8.8.8, with what each does: [zoho-header-check.md](evidence/zoho-header-check.md). Full zone: [dns-https-final.md](evidence/dns-https-final.md)

## 7. GA4

- Tag on every page: commit [`839b0c0`](https://github.com/emcgough4/career-platform/commit/839b0c0). Privacy page: [`7a3a8e9`](https://github.com/emcgough4/career-platform/commit/7a3a8e9), [`1d45d7c`](https://github.com/emcgough4/career-platform/commit/1d45d7c)
- Realtime `page_view` and outbound `click`, with the meaning of the click: [ex06.md](evidence/ex06.md) §3, 2026-10-15
- How a browser event reaches GA4, and what each check proves: [README "Analytics"](../README.md#analytics)

## 8. Failures, decisions, reflection, costs, limitations

- Application failure: [ex03.md](evidence/ex03.md) §3. `/` showed a placeholder; the fix was the redirect in [`0546382`](https://github.com/emcgough4/career-platform/commit/0546382).
- DNS/TLS failure, a deliberate lab simulation: [ex05.md](evidence/ex05.md), commit [`540e8ab`](https://github.com/emcgough4/career-platform/commit/540e8ab)
- Railway deploy failures, investigated during the migration: Railway plan Section 5 note. Railpack had no start command ([`5488a44`](https://github.com/emcgough4/career-platform/commit/5488a44)), and pip ignored `uv.lock` ([`41128da`](https://github.com/emcgough4/career-platform/commit/41128da)).
- Decisions with alternatives (Railway migration, managed vs self-hosted email): [README "Decisions"](../README.md#decisions)
- Reflection: [README "Reflection"](../README.md#reflection)
- Costs, credits, expiration dates and cleanup: [README "Costs, credits and cleanup"](../README.md#costs-credits-and-cleanup)
- Investigated failures table (symptom, checks, repair, repeated check): [README "Investigated failures"](../README.md#investigated-failures)
- Remaining limitations: [README "Limitations"](../README.md#limitations)

## 9. Final check, 2026-10-25 21:28 UTC

**Verified**

- The repository opens at https://github.com/emcgough4/career-platform, and `main` matches my local branch.
- The site serves the reviewed version. Every file in `app/`, `templates/`, `static/`, `data/`, `alembic/` and `scripts/` in the running Railway container matches the repo (56 files, `sha256sum` over `railway ssh`). The commits after `4f9fdc8` change only docs.
- `/` redirects (307) to `/about`. `/about`, `/resume`, `/portfolio`, `/contact` and `/privacy` return 200, served from the database, not the fallback. `/health` returns `{"status":"ok"}`.
- `http://www` and `https://www` redirect (301) to `https://elliemcgough.me/`. The certificate is Let's Encrypt for `elliemcgough.me` and expires 2027-01-06.
- MX (Zoho ×3), SPF and DMARC still resolve as recorded, checked against 8.8.8.8.
- The GA4 tag appears once on the live page.
- All 48 tests pass locally.

**Not verified**

- Controlled Azure VM restart, and the Azure Nginx HTTPS server block: the VM is shut off.
- A real change to the original data that seed scripts couldn't reproduce: missing (README "How current data was preserved").
- The 503 page and recovery after the database comes back, on the live site: never triggered live. There's no recovery test either; only the fallback is tested.
- The live deployment came from `railway up`, not GitHub autodeploy, so Railway records no commit hash for it. The file match above is the link to the commit.
- Email sending and receiving, and GA4 Realtime, weren't re-tested today. The evidence dates from 2026-10-15 ([ex06.md](evidence/ex06.md)). The Gmail spam result is still unresolved.
