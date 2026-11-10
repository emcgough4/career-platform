# Cutover: `elliemcgough.me` → AWS EC2

Done 2026-11-09, between 04:24 and 04:27 UTC. The plan is Section 8 of `docs/superpowers/plans/2026-11-03-aws-ec2-rds-migration.md`, and the course guide is section 11. The tests run before cutover are in `docs/evidence/aws-test-subdomain.md`.

**Starting point:** the site was already down. Since some time after 2026-11-03, `https://elliemcgough.me` had returned Railway's `404 Application not found`, because the career-platform app is gone from the Railway account. The cutover brings the site back on AWS, serving the 2026-10-29 data.

## Timeline (UTC)

| Time | Step |
| --- | --- |
| 04:24 | Step 1: RDS checksums match `backups/checksums-dump.txt`, so nothing changed since the restore |
| 04:25:07 | Step 2: the root-domain record `f895e3b8…` changed in place from CNAME `tmbs117o.up.railway.app` to A `52.71.186.61`, DNS only, TTL Auto |
| ~04:25:20 | Cloudflare's own DNS server and 1.1.1.1 answer `52.71.186.61` |
| ~04:26 | Step 3: the certificate dry run passed, then the certificate was expanded to both names and installed with `--redirect` |
| 04:26:10 | 8.8.8.8 and the laptop's `dig` answer `52.71.186.61` |
| 04:26:27 | The laptop's system resolver (curl) reaches the EC2 instance. `/about` returns 200 |

## Evidence

### DNS change (Step 2)

The zone was saved before and after the change and compared field by field:

```
before 11, after 11; removed []; added []
changed: [('elliemcgough.me', 'CNAME', '->', 'A', '52.71.186.61', 'DNS only')]
```

`www`, the redirect rule, `_railway-verify`, `aws`, MX, SPF, DKIM, DMARC and the Zoho TXT record are untouched. The record's comment notes the old value, so it's easy to undo.

```
$ nslookup elliemcgough.me
Address: 52.71.186.61
$ dig +short elliemcgough.me @8.8.8.8
52.71.186.61
```

### Certificate (Step 3)

```
Simulating renewal of an existing certificate for aws.elliemcgough.me and elliemcgough.me
The dry run was successful.
Successfully received certificate.            (expires 2027-02-08)
Successfully deployed certificate for aws.elliemcgough.me to /etc/nginx/sites-enabled/career-platform
Successfully deployed certificate for elliemcgough.me to /etc/nginx/sites-enabled/career-platform
nginx: configuration file /etc/nginx/nginx.conf test is successful
git -C /opt/career-platform status --short    → 0 lines
```

```
$ openssl s_client -connect elliemcgough.me:443 -servername elliemcgough.me | openssl x509 -noout -issuer -ext subjectAltName
issuer=C=US, O=Let's Encrypt, CN=YE2
X509v3 Subject Alternative Name: DNS:aws.elliemcgough.me, DNS:elliemcgough.me
```

On port 80, both names return 301 to `https://$host$request_uri`, and any other host gets 404.

### The real domain is on EC2 (Step 4)

```
$ curl -s -o /dev/null -w '%{http_code} via %{remote_ip}' https://elliemcgough.me/about
200 via 52.71.186.61
$ curl -s -o /dev/null -w '%{http_code} %{redirect_url}' http://elliemcgough.me/about
301 https://elliemcgough.me/about
$ curl -sI http://elliemcgough.me/
HTTP/1.1 301 Moved Permanently
Location: https://elliemcgough.me/
$ curl -sI https://www.elliemcgough.me/
HTTP/2 301
location: https://elliemcgough.me/
$ curl -sI https://elliemcgough.me/about | grep -i server
Server: nginx/1.28.3 (Ubuntu)
```

- **`og:image` on `/about`:** `https://elliemcgough.me/static/media/eleanor-mcgough.jpg`.
- **Fallback marker on `/about`:** 0.
- **Pages:** `/about`, `/contact`, `/portfolio`, `/privacy`, `/resume`, `/projects/1`, `/projects/13` and `/health` return 200, and `/no-such-page` returns 404.

## Deviations

- **No Railway comparison.** Step 1's checksum was compared with the checksums from the restore, because Railway no longer has the data.
- **The record was edited, not replaced.** The plan says "replace the CNAME with an A record". I changed the existing record's type with one `PATCH`, so the root domain never went without a record.
- **`curl -sI https://elliemcgough.me/about` returns 405, not 200.** The FastAPI routes don't accept `HEAD` (a known finding from the test-subdomain run, unchanged since Railway). The 200 check uses `GET`, and the `server: nginx` check uses the 405's headers.
- **Certbot was run as two commands.** I ran `certbot install` with `--redirect` and `--non-interactive`, so the root domain got its own HTTP→HTTPS redirect without a prompt.

## Not verified

- **The padlock in a browser**, which needs a person to look.
- **What visitors with stale DNS see.** Resolvers that cached the old CNAME go to Railway's 404 until the cache expires (TTL Auto = 300 s). It's already past that for the resolvers I checked.
- **Google Analytics recording visits after cutover.**
- **The other items in "Not verified" in `docs/evidence/aws-test-subdomain.md`:** reboot, real renewal, load, point-in-time restore, a second deploy and IPv6.

## Rollback

There's no Railway to go back to, so putting back the CNAME `tmbs117o.up.railway.app` would only bring back the 404. If the site breaks on EC2, redeploy a known-good commit with `deploy.sh <commit>`; the logs are in `journalctl -u career-platform`. If the data is wrong, restore from `backups/` or use RDS point-in-time restore (1-day retention).
