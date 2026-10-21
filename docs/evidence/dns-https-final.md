# Final DNS and HTTPS on Railway

**Captured:** October 21, 2026, 17:19 UTC (10:19 AM Pacific), from the laptop.
**Tools:** `curl`, `openssl s_client`, `dig`, Cloudflare CLI (`cf`) 1.0.0-beta.16.

This records where `elliemcgough.me` points after the move to Railway and how HTTPS works there. The Azure HTTPS setup (Nginx, certbot) is in [how-this-site-is-secured.md](../how-this-site-is-secured.md) (Exercise 04). The zone before mail setup is in [dns-before-zoho.md](dns-before-zoho.md).

## DNS records

Nameservers: `harley.ns.cloudflare.com`, `ulla.ns.cloudflare.com` (Cloudflare is authoritative).

Command: `cf dns records list --zone elliemcgough.me --per-page 5000` (10 records).

| Name | Type | Content | Proxy | Last modified | Purpose |
| --- | --- | --- | --- | --- | --- |
| `elliemcgough.me` | CNAME | `tmbs117o.up.railway.app` | DNS only | 2026-10-08 | Sends the bare domain to the Railway service. Cloudflare flattens the CNAME at the apex, so a lookup returns Railway's IP directly. DNS only means browsers connect straight to Railway, and Railway holds the certificate. |
| `_railway-verify.elliemcgough.me` | TXT | `railway-verify=a9628dcf…` | DNS only | 2026-10-08 | Proves to Railway that I control the domain. Railway requires it alongside the CNAME. |
| `www.elliemcgough.me` | A | `192.0.2.1` | Proxied | 2026-10-14 | A placeholder address (192.0.2.0/24 is reserved for documentation and never routes). Proxied means Cloudflare answers `www` itself and applies the redirect rule below, so the address is never used. |
| `elliemcgough.me` | MX | `mx.zoho.com` (10), `mx2.zoho.com` (20), `mx3.zoho.com` (50) | DNS only | 2026-10-13 | Incoming mail goes to Zoho. A lower number is tried first. |
| `elliemcgough.me` | TXT | `v=spf1 include:zohomail.com ~all` | DNS only | 2026-10-13 | SPF: Zoho's servers may send mail for the domain. |
| `zmail._domainkey.elliemcgough.me` | TXT | `v=DKIM1; k=rsa; p=MIGfMA0G…` | DNS only | 2026-10-13 | DKIM public key (selector `zmail`) used to check Zoho's signatures. |
| `_dmarc.elliemcgough.me` | TXT | `v=DMARC1; p=none; rua=mailto:ellie@elliemcgough.me` | DNS only | 2026-10-13 | DMARC: monitor only (`p=none`), with aggregate reports to my mailbox. |
| `elliemcgough.me` | TXT | `zoho-verification=zb92317202.zmverify.zoho.com` | DNS only | 2026-10-13 | Proves domain ownership to Zoho. |

Public answers from `dig +short`:

```
$ dig +short elliemcgough.me A
69.46.46.57
$ dig +short www.elliemcgough.me A
172.67.178.114
104.21.59.138
$ dig +short elliemcgough.me MX
10 mx.zoho.com.
20 mx2.zoho.com.
50 mx3.zoho.com.
```

The bare domain resolves to a Railway address. `www` resolves to Cloudflare's own addresses because it is proxied.

## www redirect rule

Railway's trial allows one custom domain, so the site's address is the bare domain and `www` is redirected by Cloudflare. The rule was read from `cf rulesets get` (phase `http_request_dynamic_redirect`):

| Field | Value |
| --- | --- |
| Description | `Redirect www` |
| Matches | `http.request.full_uri wildcard "http*://www.*"` (both `http://www…` and `https://www…`) |
| Target | `wildcard_replace(…, "http*://www.*", "https://${2}")`, which keeps the path and drops `www` |
| Status | 301, query string preserved |
| Enabled | yes, last updated 2026-10-14 00:32 UTC |

## Verification

```
$ curl -sI http://www.elliemcgough.me/
HTTP/1.1 301 Moved Permanently
Location: https://elliemcgough.me/
Server: cloudflare

$ curl -sI https://www.elliemcgough.me/
HTTP/2 301
location: https://elliemcgough.me/
server: cloudflare

$ curl -sI http://elliemcgough.me/
HTTP/1.1 301 Moved Permanently
location: https://elliemcgough.me/

$ curl -sL -o /dev/null -w "final=%{url_effective} code=%{http_code} redirects=%{num_redirects} ssl_verify=%{ssl_verify_result}\n" http://www.elliemcgough.me/
final=https://elliemcgough.me/about code=200 redirects=2 ssl_verify=0
```

Result:
- `http://www` and `https://www` both land on `https://elliemcgough.me/`.
- Following the full chain from `http://www` ends at `/about` with 200, after the site's own `/` → `/about` redirect.
- `ssl_verify=0` means curl accepted every certificate on the way.
- `curl -I` (a HEAD request) to `https://elliemcgough.me/` returns 405 from `railway-hikari`. HEAD isn't allowed by the app (also true on the VM), so the GET above is the real check.

## Certificates

```
$ echo | openssl s_client -connect elliemcgough.me:443 -servername elliemcgough.me | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
subject=CN=elliemcgough.me
issuer=C=US, O=Let's Encrypt, CN=YR2
notBefore=Oct  8 22:05:27 2026 GMT
notAfter=Jan  6 22:05:26 2027 GMT
X509v3 Subject Alternative Name:
    DNS:elliemcgough.me

$ echo | openssl s_client -connect www.elliemcgough.me:443 -servername www.elliemcgough.me | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
subject=CN=elliemcgough.me
issuer=C=US, O=Let's Encrypt, CN=YE1
notBefore=Oct  1 21:02:40 2026 GMT
notAfter=Dec 30 21:02:39 2026 GMT
X509v3 Subject Alternative Name:
    DNS:*.elliemcgough.me, DNS:elliemcgough.me
```

There are two certificates, held by two different services:

| Hostname | Served by | Certificate | Valid | Renewal |
| --- | --- | --- | --- | --- |
| `elliemcgough.me` | Railway's edge (DNS only, so the browser connects to Railway directly) | Let's Encrypt (YR2), covers only `elliemcgough.me` | Oct 8, 2026 to Jan 6, 2027 (90 days) | Railway issues it when the custom domain is verified and renews it automatically. Its docs say custom domains get "automatic SSL certificate provisioning" and that certificates are "automatically provisioned and renewed" ([working with domains](https://docs.railway.com/networking/domains/working-with-domains), [public networking](https://docs.railway.com/guides/public-networking)). There is no certbot to manage. |
| `www.elliemcgough.me` | Cloudflare's edge (proxied) | Cloudflare Universal SSL from Let's Encrypt (YE1), covers `*.elliemcgough.me` and `elliemcgough.me` | Oct 1, 2026 to Dec 30, 2026 | Cloudflare renews Universal SSL certificates automatically. This one only has to be valid long enough to send the redirect. |

TLS for the site ends at Railway's edge, which forwards plain HTTP to the app on Railway's private network. That is why uvicorn trusts forwarded headers (`X-Forwarded-Proto`) and why the app's links come out as `https://`. On Azure, TLS ended at Nginx on the VM.

**Unverified:** Railway's renewal hasn't happened yet. The first renewal should come before January 6, 2027. To check it then, rerun the `openssl` command for `elliemcgough.me` and confirm `notAfter` has moved later.
