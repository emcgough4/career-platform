# Project 1 gaps

Found in a repository audit on 2026-10-20 against the Project 1 requirements. Each line names the file or check that closes it.

> **2026-10-21: not every gap can be closed before submission, because Railway was having problems.** These are waiting on Railway:
> - The real-profile snapshot refresh. `data/public_profile_snapshot.json` is still the placeholder ("Your Name"), so a database outage shows that instead of my profile.
> - The dated live check of database recovery.
>
> The 503 fallback code and its tests are done (48 passing) and pushed, but Railway hadn't deployed that push as of 2026-10-22 18:34 UTC ([railway-deploy.md](docs/evidence/railway-deploy.md)). The Azure items can't be closed either, because the VM is shut off.

## 1. Profile and project data

- [ ] On a database failure, show the real profile plus "Projects temporarily unavailable" with HTTP 503 instead of the 200 snapshot fallback — `app/services/profile_service.py`, routes, `templates/portfolio.html`, and update `tests/test_fallback.py`
- [ ] Prove projects return after the database recovers, without an app restart — new test plus a dated live check
- [ ] Explain the initial database engine choice (SQLite) and why — README decisions section
- [x] Confirm live content has education, professional links, labeled placeholders, and a "this website, in progress" project entry — check the live `/about`, `/resume`, `/portfolio`
  > **Checked 2026-10-21 17:10 UTC:** `/about`, `/resume`, `/portfolio`, `/contact` all 200, no fallback marker. Name, summary, and education (Loyola Marymount University, double degree, Class of May 2027) are present. Links are LinkedIn on `/contact` and email `mailto:elliemcg30@gmail.com`. 13 real projects, so no placeholders are needed. Follow-ups: no "this website, in progress" project entry (the requirements call it useful, not required), and the site's email is Gmail rather than `ellie@elliemcgough.me`.

## 2. Azure deployment

- [ ] Run and record a controlled VM restart showing the site responds and reads its database afterward — dated output in `docs/evidence/`
  > **2026-10-21:** The Azure VM is permanently shut off, so this can no longer be run or captured. Mark it unverified in the README and submission index rather than filling in an expected result.
- [x] Explain which configuration makes the site come back after a restart (systemd `enable`, nginx service, DB path) — README Azure section
  > **2026-10-21:** README "Earlier host: Azure VM" → "What brings the site back after a restart". Marked as written afterward; the reboot itself is listed as unverified.
- [ ] Record the Nginx HTTPS/certbot server block — `docs/how-this-site-is-secured.md` or the operate-the-VM plan
  > **2026-10-21:** The Azure VM is permanently shut off, so this can no longer be run or captured. Mark it unverified in the README and submission index rather than filling in an expected result.
- [ ] Confirm the Azure VM is still running — `az vm show` or the portal
  > **2026-10-21:** The Azure VM is permanently shut off, so this can no longer be run or captured. Mark it unverified in the README and submission index rather than filling in an expected result.

## 3. Domain and HTTPS

- [x] Record the Cloudflare `www` redirect rule and verify `http://www` and `https://www` land on the root with a valid cert — dated `curl -I` output in `docs/evidence/`
  > **2026-10-21:** `docs/evidence/dns-https-final.md`.
- [x] Explain Railway's certificate hostname, validity, and renewal — README or `docs/how-this-site-is-secured.md`
  > **2026-10-21:** `docs/evidence/dns-https-final.md`.
- [x] List the final DNS records and their purpose — current `cf dns records list` output in `docs/evidence/`
  > **2026-10-21:** `docs/evidence/dns-https-final.md`.
- [x] Update `docs/how-this-site-is-secured.md` for Railway (it still describes the Azure setup)
  > **2026-10-21:** Not rewritten. It is the Exercise 04 explanation, which the requirements say to link rather than replace. The Railway HTTPS record is in `docs/evidence/dns-https-final.md` instead, and that file links back to it.

## 4. Railway and PostgreSQL migration

- [x] Add the Railway migration spec under `docs/superpowers/specs/` (the plan cites only "the request in chat")
  > **2026-10-21:** Not created. No spec was written at the time, and making one now would look like it came before the work. The README and submission index say the plan's "Spec" line quotes the request.
- [x] Tick or annotate Sections 4, 7 and 8 and record the out-of-order cutover — `docs/superpowers/plans/2026-10-08-railway-postgres-migration.md`
  > **2026-10-21:** Notes added under Sections 4, 7 and 8, labeled as recorded afterward, with the timeline from git and Cloudflare timestamps.
- [ ] Record one real change to the original project data that seed scripts can't reproduce, and show it on Railway — migration evidence
  > **2026-10-21:** Can't be closed. The "WordPress" skill was probably added on Railway after cutover (the user doesn't remember), so it isn't evidence of a pre-migration change, and the VM is shut off. Recorded as missing in the README and submission index.
- [x] Write a rollback procedure that covers data written after cutover — README rollback section
  > **2026-10-21:** README "Rollback" (code, schema, data, and the cutover-era VM path).
- [x] Compare who manages OS, runtime, web entry, TLS, code, config, DB software, data and DNS on Azure vs Railway — README responsibilities section
  > **2026-10-21:** README "Who manages what".
- [x] Link the Railway spec and plan from the README and the submission index
  > **2026-10-21:** The plan is linked from both. There is no spec file (see above).

## 5. Reviewed change through Railway

- [x] Connect one reviewed commit SHA to its Railway deployment ID and the live behavior at the domain — dated evidence file
  > **2026-10-22:** `docs/evidence/railway-deploy.md`. `839b0c0` → deployment `3ddcbf11`, GA4 tag live once on the page. The user reviewed the Google Analytics change in class.
- [x] Confirm GitHub autodeploy and its branch in Railway — screenshot or `railway deployment list` output
  > **2026-10-22:** `railway deployment list` shows a deployment per push on `main` ([railway-deploy.md](docs/evidence/railway-deploy.md)).
- [x] Explain restoring a previous version for code and for database changes — README rollback section
  > **2026-10-21:** README "Rollback".

## 6. Zoho email

- [x] Create `docs/evidence/zoho-header-check.md` with the header analysis
  > **2026-10-21:** Created from the Test 04 header excerpt in `ex06.md`.
- [x] Add the before-MX message line and what happened to it — `docs/evidence/ex06.md`
  > **2026-10-21:** "Before MX" row added to `ex06.md` §1, from the user's account: "It never arrived".
- [x] Record and explain final MX, SPF, DKIM and DMARC records — DNS output plus explanation in `docs/evidence/`
  > **2026-10-21:** `zoho-header-check.md` (checked against 8.8.8.8) and `dns-https-final.md`.
- [x] Note that Gmail showed `ellie@elliemcgough.me` as the reply's sender — `docs/evidence/ex06.md`
  > **2026-10-21:** Recorded in `ex06.md` §1, along with the spam result, marked unresolved with the check that would close it.
- [x] Link `ex06.md` and `zoho-header-check.md` from the README and the submission index
  > **2026-10-21:** README "Email" section and submission index section 6.

## 7. GA4

- [x] Explain how a browser event reaches GA4 (gtag.js → dataLayer → collect request) — README or `docs/evidence/ex06.md`
  > **2026-10-21:** README "Analytics" → "How a visit reaches Google Analytics".
- [x] State the action performed, the event observed, and what each check proves — `docs/evidence/ex06.md`
  > **2026-10-21:** README "Analytics" → "What the checks show". The user confirmed making the 3 clicks.

## 8. Engineering record

- [x] Create `docs/project-1-submission.md` with the repo URL, live URL, final commit SHA and the eight link groups
  > **2026-10-22:** Final commit `43456c7`. The items it marks **Not yet recorded** are the ones that couldn't be closed (Azure VM off, Railway not deploying).
- [x] Add Azure and Railway architecture diagrams with locations, protocols, ports, data flow, email and analytics paths — README or a linked diagram file
  > **2026-10-21:** README "Architecture" (two Mermaid diagrams).
- [x] Add a rollback section for code and data — README
  > **2026-10-21:** README "Rollback".
- [x] Explain how the migration preserved current data and which responsibilities moved to Railway — README
  > **2026-10-21:** README "How current data was preserved" and "Who manages what".
- [x] Add at least two decisions with alternatives (Railway migration, managed vs self-hosted email) — README
  > **2026-10-21:** README "Decisions", with the reasons in the user's words.
- [x] Link the two investigated failures (`docs/evidence/ex03.md`, `docs/evidence/ex05.md`) and strengthen the Ex03 repeated check — README failures section
  > **2026-10-21:** README "Investigated failures". The Ex03 repeated check comes from the Azure plan's 2026-09-29 note (failing-then-passing test, plus the VM check). `ex03.md` itself is unchanged.
- [x] Add remaining limitations — README
  > **2026-10-21:** README "Limitations".
- [x] Add a short reflection — README
  > **2026-10-21:** README "Reflection", in the user's words.
- [x] Record service costs/credits, the Railway trial end date, renewal dates and cleanup plans — README costs section
  > **2026-10-21:** README "Costs, credits and cleanup". Balances from the user, resource states from `az` and `whois`.
- [x] Remove the stale "www still points at the old Azure VM" line — README
  > **2026-10-21:** README "How it runs" DNS paragraph rewritten.
