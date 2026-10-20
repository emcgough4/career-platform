# Request path: what happens when I enter my domain in a browser

Study diagram for the midterm, drafted with Claude Code on 2026-10-20. Anything the
repository doesn't record is marked **unknown** or **assumed**. Facts come from the
README, `docs/how-this-site-is-secured.md`, `docs/evidence/dns-before-zoho.md`,
and the Azure and Railway plans under `docs/superpowers/plans/`.

## 1. Hardware with the Railway services on it (current host)

```mermaid
flowchart LR
  subgraph HOME["Home network: private addresses (Ex01 values not in repo)"]
    direction LR
    LAP["Laptop<br/>browser = software<br/>NIC: private IP, subnet,<br/>gateway, DNS server via DHCP"]
    subgraph BOX["Home router box: roles share one device (confirm on its label)"]
      AP["Wi-Fi access point"]
      SW["Switch: same-network traffic"]
      RT["Router: default gateway<br/>NAT private ⇄ public<br/>stateful firewall (unknown)<br/>DHCP server"]
    end
    MOD["Modem or fiber box (unknown which)"]
  end

  ISP["ISP (unknown)"]
  NET["Internet routers"]

  subgraph DNS["DNS: a separate exchange"]
    RES["Recursive resolver<br/>(the DNS server from DHCP)"]
    CF["Cloudflare authoritative<br/>harley / ulla.ns.cloudflare.com<br/>elliemcgough.me CNAME → Railway, DNS only"]
  end

  subgraph RW["Railway: project astonishing-vision"]
    EDGE["Railway edge<br/>public :443<br/>TLS ENDS HERE<br/>Let's Encrypt cert to 2027-01-06"]
    APP["career-platform<br/>uvicorn 0.0.0.0:$PORT (8080)<br/>trusts forwarded headers"]
    PG[("Postgres<br/>postgres.railway.internal<br/>port 5432 assumed")]
  end

  LAP -- "Wi-Fi" --- AP --- SW --- RT --- MOD --- ISP --- NET
  LAP -. "① DNS query UDP 53" .-> RES
  RES -. "② asks authoritative" .-> CF
  NET -- "③ TCP 443 + TLS<br/>src = home public IP after NAT" --> EDGE
  EDGE -- "④ plain HTTP, private network" --> APP
  APP -- "⑤ SQL, private network" --> PG
```

## 2. One page load in order (client → server on each line)

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser (laptop)
  participant R as Home router (NAT)
  participant D as DNS resolver
  participant C as Cloudflare DNS
  participant E as Railway edge
  participant A as App (uvicorn)
  participant P as Postgres

  Note over B: Assume a new HTTPS connection, no cached DNS, typed without https
  B->>D: Where is elliemcgough.me? (UDP 53)
  D->>C: Recursive lookup
  C-->>D: CNAME → Railway, then its A record
  D-->>B: Railway's public IP
  B->>R: TCP to Railway IP:80, src = private IP
  R->>E: NAT rewrites src to home public IP
  E-->>B: Redirect to https://
  B->>E: TCP 443 handshake, then TLS
  E-->>B: Certificate: hostname, dates, chain checked
  Note over B,E: Encrypted from browser to edge. TLS ends at the edge.
  B->>E: GET /  (HTTPS)
  E->>A: GET / plain HTTP + X-Forwarded-Proto: https
  A-->>E: 307 → /about
  E-->>B: Redirect
  B->>E: GET /about
  E->>A: GET /about
  A->>P: SELECT profile, projects (each request)
  P-->>A: Rows
  A-->>E: 200 HTML
  E-->>R: Response to home public IP
  R-->>B: NAT maps reply back to the laptop
  B->>E: Separate requests: /static CSS, JS, images
  B->>B: gtag.js loads from googletagmanager.com (a separate host, its own DNS + TLS)
```

## 3. What changes on Azure

```mermaid
flowchart LR
  NET["Internet"] -- "TCP 443" --> NSG
  subgraph AZ["Azure VM vm-career-platform<br/>public 172.214.156.151 / private 10.0.0.4"]
    NSG["Network security group<br/>22 from 2 /32s only<br/>80 and 443 from any<br/>no rule for 8000"]
    NGX["Nginx :80 / :443<br/>TLS ENDS HERE<br/>certbot renews"]
    UV["uvicorn 127.0.0.1:8000<br/>2 workers, systemd"]
    DB[("SQLite file<br/>data/career_platform.db")]
    NSG --> NGX
    NGX -- "plain HTTP, loopback" --> UV
    UV -- "file read, no network" --> DB
  end
```

On Azure, DNS was an A record pointing to the VM's public IP, not a CNAME.

## Unverified

- Home equipment, ISP and Exercise 01 addresses are placeholders.
- Postgres on port 5432 is the default, not confirmed.
- The http → https redirect on Railway is the study guide's assumption, not a recorded check.
- The `307` from `/` to `/about` comes from `app/main.py`.
