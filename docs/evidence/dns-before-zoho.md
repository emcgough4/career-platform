# DNS records before Zoho Mail setup

**Captured:** October 13, 2026, 21:10 UTC (2:10 PM Pacific)  
**Zone:** `elliemcgough.me` (status: active)  
**Nameservers:** `harley.ns.cloudflare.com`, `ulla.ns.cloudflare.com`  
**Tool:** Cloudflare CLI (`cf`) 1.0.0-beta.16

This is a snapshot of every DNS record in the zone before any Zoho Mail
records are added, so the change can be compared or rolled back later.

## Command

```
cf dns records list --zone elliemcgough.me --per-page 5000
```

The command returned 3 records.

## Records

| Name | Type | Content | Proxy status | TTL |
|------|------|---------|--------------|-----|
| `www.elliemcgough.me` | A | `192.0.2.1` | Proxied | Auto |
| `elliemcgough.me` | CNAME | `tmbs117o.up.railway.app` | DNS only | Auto |
| `_railway-verify.elliemcgough.me` | TXT | `"railway-verify=a9628dcf34179468ad50058dfb97b24d761c96e53363442994439d5652206362"` | DNS only | Auto |

There are no MX records and no mail-related TXT records (SPF, DKIM, DMARC) in
the zone yet.

## Raw output

```json
[
  {
    "id": "40618ea994a65b71a3f6dd1567039ec7",
    "name": "www.elliemcgough.me",
    "type": "A",
    "content": "192.0.2.1",
    "proxiable": true,
    "proxied": true,
    "ttl": 1,
    "settings": {},
    "meta": {},
    "comment": null,
    "tags": [],
    "created_on": "2026-10-01T21:41:14.351854Z",
    "modified_on": "2026-10-13T21:08:33.186042Z"
  },
  {
    "id": "f895e3b87df3bfd405760f9112110581",
    "name": "elliemcgough.me",
    "type": "CNAME",
    "content": "tmbs117o.up.railway.app",
    "proxiable": true,
    "proxied": false,
    "ttl": 1,
    "settings": {
      "flatten_cname": false
    },
    "meta": {},
    "comment": null,
    "tags": [],
    "created_on": "2026-10-08T23:00:48.123105Z",
    "modified_on": "2026-10-08T23:00:48.123105Z"
  },
  {
    "id": "3f3409db422321fdcd6c347e65554a0f",
    "name": "_railway-verify.elliemcgough.me",
    "type": "TXT",
    "content": "\"railway-verify=a9628dcf34179468ad50058dfb97b24d761c96e53363442994439d5652206362\"",
    "proxiable": false,
    "proxied": false,
    "ttl": 1,
    "settings": {},
    "meta": {},
    "comment": null,
    "tags": [],
    "created_on": "2026-10-08T22:55:42.544686Z",
    "modified_on": "2026-10-08T22:55:42.544686Z"
  }
]
```
