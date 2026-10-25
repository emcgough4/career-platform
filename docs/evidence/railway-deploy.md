# One change through Railway: commit, deployment, live result

**Checked:** 2026-10-22, 18:34 UTC. The deployment list comes from `railway deployment list --service career-platform --json` (project `astonishing-vision`, environment `production`).

## The change

[`839b0c0`](https://github.com/emcgough4/career-platform/commit/839b0c0) "feat: load the GA4 Google tag once on every page", committed Oct 15, 2026 at 15:06:38 PDT (22:06:38 UTC).

- **What it changes:** it adds the `gtag.js` snippet for `G-QX9JPW5PPP` to `templates/base.html`, which every page extends.
- **How it was tested:** a test in `tests/test_contact_and_layout.py` checks that the tag appears exactly once per page.
- **Review:** in my words, "I reviewed Google Analytics in class." When that review happened relative to the push wasn't recorded.

## The deployment

| Deployment ID | Status | Created (UTC) | Commit | Branch |
| --- | --- | --- | --- | --- |
| `3ddcbf11-47ed-44e6-80a3-11693a677851` | REMOVED (replaced by later deploys) | 2026-10-15 22:06:41 | `839b0c0` | `main` |

Railway created the deployment 3 seconds after the commit. This confirms that GitHub autodeploy is on for `main`: every push since Oct 8 has its own deployment with that commit's hash and branch. "REMOVED" means a newer deployment replaced this one, not that the deployment failed.

The deployment serving the site now:

| Deployment ID | Status | Created (UTC) | Commit |
| --- | --- | --- | --- |
| `a5feba6e-420c-46a3-a85b-c61028abbe06` | SUCCESS | 2026-10-20 21:43:22 | `a2129dc` (contains `839b0c0`) |

## The live result

At 2026-10-22 18:34 UTC:

```
$ curl -s https://elliemcgough.me/about | grep -o 'googletagmanager.com/gtag/js?id=G-[A-Z0-9]*' | sort | uniq -c
   1 googletagmanager.com/gtag/js?id=G-QX9JPW5PPP
$ curl -s https://elliemcgough.me/health
{"status":"ok"}
```

The tag appears exactly once on the live page, which matches the test. GA4 Realtime then recorded `page_view` and `click` events from the live site on Oct 15 ([ex06.md](ex06.md) §3).

## Pushes not yet deployed

[`7a10530`](https://github.com/emcgough4/career-platform/commit/7a10530) (the 503 database-failure page) and [`d8b6985`](https://github.com/emcgough4/career-platform/commit/d8b6985) (docs) were pushed on 2026-10-21. As of this check, Railway had no deployment for either, because Railway was having problems at the time. The live site still runs `a2129dc`, so the 503 behavior is tested locally but not live.

## Update, 2026-10-25 21:28 UTC

The 503 change and the refreshed snapshot are now live, but they did not arrive through GitHub autodeploy:

| Deployment ID | Status | Created (UTC) | Source |
| --- | --- | --- | --- |
| `8c8479d1-8b72-4420-ae6a-2a3e0096d6d3` | REMOVED (replaced) | 2026-10-24 00:20:31 | GitHub push of `4f9fdc8` |
| `8d5efc20-c352-409e-8085-2e32157b57a8` | SUCCESS | 2026-10-24 00:26:16 | `railway up` from the local tree (no commit hash) |

Because `8d5efc20` has no commit hash, I checked the running container directly. `railway ssh` ran `sha256sum` over every file in `app/`, `templates/`, `static/`, `data/`, `alembic/` and `scripts/`, and all 56 matched the same files at `4f9fdc8`. The live `/static/css/styles.css` and `/static/js/site.js` are byte-identical to the repo, `/health` returns `{"status":"ok"}`, and `/about` doesn't show the fallback notice.

What this doesn't show: the 503 page itself has not been triggered on the live site. Only the tests cover it.
