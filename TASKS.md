# Project 1 gaps

Found in a repository audit on 2026-10-20 against the Project 1 requirements. Each line names the file or check that closes it.

## 1. Profile and project data

- [ ] On a database failure, show the real profile plus "Projects temporarily unavailable" with HTTP 503 instead of the 200 snapshot fallback — `app/services/profile_service.py`, routes, `templates/portfolio.html`, and update `tests/test_fallback.py`
- [ ] Prove projects return after the database recovers, without an app restart — new test plus a dated live check
- [ ] Explain the initial database engine choice (SQLite) and why — README decisions section
- [ ] Confirm live content has education, professional links, labeled placeholders, and a "this website, in progress" project entry — check the live `/about`, `/resume`, `/portfolio`

## 2. Azure deployment

- [ ] Run and record a controlled VM restart showing the site responds and reads its database afterward — dated output in `docs/evidence/`
- [ ] Explain which configuration makes the site come back after a restart (systemd `enable`, nginx service, DB path) — README Azure section
- [ ] Record the Nginx HTTPS/certbot server block — `docs/how-this-site-is-secured.md` or the operate-the-VM plan
- [ ] Confirm the Azure VM is still running — `az vm show` or the portal

## 3. Domain and HTTPS

- [ ] Record the Cloudflare `www` redirect rule and verify `http://www` and `https://www` land on the root with a valid cert — dated `curl -I` output in `docs/evidence/`
- [ ] Explain Railway's certificate hostname, validity, and renewal — README or `docs/how-this-site-is-secured.md`
- [ ] List the final DNS records and their purpose — current `cf dns records list` output in `docs/evidence/`
- [ ] Update `docs/how-this-site-is-secured.md` for Railway (it still describes the Azure setup)

## 4. Railway and PostgreSQL migration

- [ ] Add the Railway migration spec under `docs/superpowers/specs/` (the plan cites only "the request in chat")
- [ ] Tick or annotate Sections 4, 7 and 8 and record the out-of-order cutover — `docs/superpowers/plans/2026-10-08-railway-postgres-migration.md`
- [ ] Record one real change to the original project data that seed scripts can't reproduce, and show it on Railway — migration evidence
- [ ] Write a rollback procedure that covers data written after cutover — README rollback section
- [ ] Compare who manages OS, runtime, web entry, TLS, code, config, DB software, data and DNS on Azure vs Railway — README responsibilities section
- [ ] Link the Railway spec and plan from the README and the submission index

## 5. Reviewed change through Railway

- [ ] Connect one reviewed commit SHA to its Railway deployment ID and the live behavior at the domain — dated evidence file
- [ ] Confirm GitHub autodeploy and its branch in Railway — screenshot or `railway deployment list` output
- [ ] Explain restoring a previous version for code and for database changes — README rollback section

## 6. Zoho email

- [ ] Create `docs/evidence/zoho-header-check.md` with the header analysis
- [ ] Add the before-MX message line and what happened to it — `docs/evidence/ex06.md`
- [ ] Record and explain final MX, SPF, DKIM and DMARC records — DNS output plus explanation in `docs/evidence/`
- [ ] Note that Gmail showed `ellie@elliemcgough.me` as the reply's sender — `docs/evidence/ex06.md`
- [ ] Link `ex06.md` and `zoho-header-check.md` from the README and the submission index

## 7. GA4

- [ ] Explain how a browser event reaches GA4 (gtag.js → dataLayer → collect request) — README or `docs/evidence/ex06.md`
- [ ] State the action performed, the event observed, and what each check proves — `docs/evidence/ex06.md`

## 8. Engineering record

- [ ] Create `docs/project-1-submission.md` with the repo URL, live URL, final commit SHA and the eight link groups
- [ ] Add Azure and Railway architecture diagrams with locations, protocols, ports, data flow, email and analytics paths — README or a linked diagram file
- [ ] Add a rollback section for code and data — README
- [ ] Explain how the migration preserved current data and which responsibilities moved to Railway — README
- [ ] Add at least two decisions with alternatives (Railway migration, managed vs self-hosted email) — README
- [ ] Link the two investigated failures (`docs/evidence/ex03.md`, `docs/evidence/ex05.md`) and strengthen the Ex03 repeated check — README failures section
- [ ] Add remaining limitations — README
- [ ] Add a short reflection — README
- [ ] Record service costs/credits, the Railway trial end date, renewal dates and cleanup plans — README costs section
- [ ] Remove the stale "www still points at the old Azure VM" line — README
