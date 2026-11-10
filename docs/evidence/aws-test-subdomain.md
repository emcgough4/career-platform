# AWS test subdomain: `https://aws.elliemcgough.me`

Tested 2026-11-09, between 04:00 and 04:30 UTC, from the laptop. The plan is Section 7 of `docs/superpowers/plans/2026-11-03-aws-ec2-rds-migration.md`, and the course guide is section 10.

- **What runs there:** EC2 `i-08b123d5a33f3a6eb` (t3.micro, Ubuntu 26.04, Elastic IP `52.71.186.61`) runs nginx and uvicorn as `career-app`, at commit `ceaf1ed`.
- **Database:** RDS `career-platform-db` (PostgreSQL 18.6, Single-AZ). The app connects as the read-only role `career_app`.
- **Data:** `backups/railway-postgres-20261029T215819Z.dump` (see `docs/migration-notes.md`).

The laptop's IP address and any database passwords are left out on purpose.

## Summary

| # | Test | Result |
| --- | --- | --- |
| 1 | DNS: `aws` resolves to the Elastic IP | Pass |
| 2 | HTTPS certificate is valid and auto-renews | Pass |
| 3 | HTTP redirects to HTTPS | Pass |
| 4 | Every page is identical to a baseline built from the same data | Pass, 19 of 19 |
| 5 | Every static file loads | Pass, 18 of 18 |
| 6 | Social preview image (`og:image`) uses `https://`, even with a spoofed header | Pass |
| 7 | Database outage gives a fast 503, then recovers without a restart | Pass |
| 8 | Only nginx is reachable from the internet; RDS is private | Pass |
| 9 | Only TLS 1.2 and 1.3 are accepted | Pass |
| 10 | Server health: no app errors, memory and disk headroom, services enabled | Pass |

## Evidence

### 1. DNS

```
$ nslookup aws.elliemcgough.me
Name:    aws.elliemcgough.me
Address: 52.71.186.61
```

The record also resolves to `52.71.186.61` on 1.1.1.1, 8.8.8.8 and Cloudflare's own DNS server for the domain. The record is DNS only (grey cloud), and the zone's other 10 records are unchanged (before-and-after diff, Section 7 Step 1).

### 2. Certificate

```
$ openssl s_client -connect aws.elliemcgough.me:443 -servername aws.elliemcgough.me | openssl x509 -noout -issuer -subject -enddate
issuer=C=US, O=Let's Encrypt, CN=YE1
subject=CN=aws.elliemcgough.me
notAfter=Feb  8 03:14:40 2027 GMT
$ curl -s -o /dev/null -w '%{ssl_verify_result}' https://aws.elliemcgough.me/health
0
$ sudo certbot renew --dry-run
Congratulations, all simulated renewals succeeded
```

`certbot.timer` is enabled and active.

### 3. HTTP redirects to HTTPS

```
$ curl -sI http://aws.elliemcgough.me/
HTTP/1.1 301 Moved Permanently
Location: https://aws.elliemcgough.me/
$ curl -s -o /dev/null -w '%{http_code} %{redirect_url}' http://aws.elliemcgough.me/about
301 https://aws.elliemcgough.me/about
```

### 4. Every page matches the baseline

**Baseline:** the plan compared each page with Railway, but the Railway app no longer exists (`404 Application not found`). Instead, I ran the **same commit** on the laptop (`app/` has no changes between `ceaf1ed` and HEAD) against a temporary local Postgres 18, restored from the **same dump**. Both sides were normalized with `sed -E 's#https://(aws\.)?elliemcgough\.me##g; s#http://127\.0\.0\.1:8001##g'` and compared with `diff`. The project IDs come from `select id from projects` on RDS (1–13).

| Path | AWS | Baseline | Diff lines | Fallback marker |
| --- | --- | --- | --- | --- |
| `/about` | 200 | 200 | 0 | 0 |
| `/resume` | 200 | 200 | 0 | 0 |
| `/portfolio` | 200 | 200 | 0 | 0 |
| `/contact` | 200 | 200 | 0 | 0 |
| `/privacy` | 200 | 200 | 0 | 0 |
| `/no-such-page` | 404 | 404 | 0 | 0 |
| `/projects/1` … `/projects/13` | 200 (each) | 200 (each) | 0 (each) | 0 (each) |

`/` returns `307` → `/about`, and `/health` returns `{"status":"ok"}`.

### 5. Static files

All 18 `/static/…` files referenced by those pages return `200` with the right content type: 1 font, 14 JPEGs, the favicon SVG, `styles.css` and `site.js`.

### 6. `og:image` and forwarded headers

```
$ curl -s https://aws.elliemcgough.me/about | grep -o '<meta property="og:image" content="[^"]*"'
<meta property="og:image" content="https://aws.elliemcgough.me/static/media/eleanor-mcgough.jpg"
$ curl -s -H 'X-Forwarded-Proto: http' https://aws.elliemcgough.me/about | grep -o 'og:image" content="[a-z]*://'
og:image" content="https://
```

nginx replaces the client's `X-Forwarded-Proto` with its own value, and uvicorn trusts only `127.0.0.1`.

### 7. Database outage

**Method:**
1. Revoke the only ingress rule on the DB security group `sg-0d2918f4b6db4e9a3` (tcp 5432 from `sg-0e35c236b5e8b76c1`), then restart the service.
2. Fetch `/about` three times.
3. Put the same rule back, wait 10 s, and fetch three more times **without** restarting.

```
T0 04:21:55 baseline: 200 0.349409s
revoke: True
outage 1 04:22:05: 503 5.302729s marker=1
outage 2 04:22:10: 503 5.248448s marker=1
outage 3 04:22:16: 503 5.255129s marker=1
health during outage: {"status":"ok"} 200
re-authorize: True
after 1 04:22:27: 200 0.363274s marker=0
after 2 04:22:28: 200 0.320912s marker=0
after 3 04:22:28: 200 0.321443s marker=0
```

During the outage, every request got a `503` with the snapshot fallback in about 5.3 s, which is `connect_timeout=5` doing its job and well within the 15 s limit. After the rule came back, pages returned to 200 by themselves. The rule was checked afterwards: `tcp 5432 5432 sg-0e35c236b5e8b76c1 from-web-sg`. Its rule ID is new, but its content is the same as before.

### 8. Exposure

```
uvicorn :8000 from internet: no connection (curl timeout)
RDS DNS from laptop: 172.31.10.19          (private address)
RDS 5432 from laptop: unreachable
RDS public=False encrypted=True multiAZ=False status=available
web SG ingress: 22 from the laptop's /32 only (laptop-2026-11-09), 80 and 443 from 0.0.0.0/0
```

### 9. TLS versions

```
tls1 refused, tls1_1 refused, tls1_2 accepted, tls1_3 accepted
```

### 10. Server health (after the tests)

- **App log:** `journalctl -u career-platform --since -15min` has 0 lines matching `traceback|error`.
- **Memory:** 372 MB available out of 908 MB.
- **Disk:** 14% of 19 GB used.
- **Services:** `career-platform`, `nginx` and `certbot.timer` are all enabled.

## Findings (not failures, nothing changed)

- **`HEAD` requests get `405 Method Not Allowed`** (as JSON), because the FastAPI routes are GET-only. This is the same code that ran on Railway. Some uptime monitors and link checkers send `HEAD`, so pick a monitor that uses `GET`.
- **No HSTS header.** HTTPS works and HTTP redirects, but browsers aren't told to insist on HTTPS. Leave it off until the root domain is on AWS, then decide.
- **`/health` doesn't check the database.** It returned 200 during the outage, so a health check alone won't spot a database problem; `/about` will (503).
- **The `Server` header shows the nginx version** (`nginx/1.28.3 (Ubuntu)`). It's minor; `server_tokens off;` would hide it.
- **HTTPS on the bare IP** serves the `aws.elliemcgough.me` certificate, because 443 has only one server block. Browsers warn about the name mismatch. It's harmless.

## Not verified

- **What visitors would see in a browser:** I didn't look at the pages in a real browser (padlock, layout, fonts, images, mobile), only at their HTML and status codes. Opening `https://aws.elliemcgough.me` on a laptop and a phone would cover it.
- **Matching the old live site:** this can't be checked any more, because Railway's app is gone. The test shows AWS matches the **2026-10-29 data**, not whatever the live site showed later. Any content edits made after 2026-10-29 are missing.
- **Google Analytics:** I didn't check whether GA4 records visits from the new host (`docs/evidence/ex06.md`).
- **Reboot survival:** the instance wasn't rebooted. The services are enabled, but I haven't seen them come back on their own.
- **A real certificate renewal:** only the dry run was tested. The first real renewal is due around 2027-01-09.
- **Load:** I didn't test concurrent traffic or the t3.micro's CPU-credit behavior. Every test was a single request.
- **Recovering the database:** I haven't tested a point-in-time restore. Retention is 1 day on the Free plan.
- **A second deploy:** `deploy.sh` has run only once. Deploying a new commit and rolling back haven't been tried.
- **The root domain:** `elliemcgough.me` still points at Railway (where it returns 404). Its certificate and redirect are part of the cutover (plan Section 8).
- **IPv6:** the instance has no IPv6 address and there's no AAAA record, so only IPv4 was tested.
- **Monitoring:** no alerts are set up for downtime or errors.
