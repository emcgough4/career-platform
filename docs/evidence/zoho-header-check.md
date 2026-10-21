# Zoho header check

**Message:** "Test 04: Outbound via Zoho MCP", from `ellie@elliemcgough.me` to my Gmail address. Gmail received it on October 15, 2026 at 2:33:37 PM PDT from `sender5-of-o52.zoho.com` (165.173.182.52). This is the new outgoing message in [ex06.md](ex06.md). The header was copied from Gmail's "Show original" on October 15. The message body is left out.

**Header analysis written:** October 21, 2026, from the excerpt saved in `ex06.md`.

## What the receiver decided

```
Authentication-Results: mx.google.com;
       dkim=pass header.i=@elliemcgough.me header.s=zmail header.b=nNrvEUMK;
       arc=pass (i=1 spf=pass spfdomain=elliemcgough.me dkim=pass dkdomain=elliemcgough.me dmarc=pass fromdomain=elliemcgough.me>);
       spf=pass (google.com: domain of ellie@elliemcgough.me designates 165.173.182.52 as permitted sender) smtp.mailfrom=ellie@elliemcgough.me;
       dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=elliemcgough.me
```

| Check | Result | What it checked | Domain it named |
| --- | --- | --- | --- |
| SPF | pass | Whether the sending server, 165.173.182.52, is allowed by the envelope sender's domain. That IP is covered by `include:zohomail.com`. | `elliemcgough.me`, from the envelope sender `smtp.mailfrom=ellie@elliemcgough.me` |
| DKIM | pass | Whether the signature in the header matches the public key published at the `zmail` selector, so the signed parts weren't changed in transit | `elliemcgough.me` (`header.i=@elliemcgough.me`, selector `header.s=zmail`) |
| DMARC | pass | Whether a passing SPF or DKIM domain matches the domain in the visible From address, and what to do if not | `elliemcgough.me` (`header.from`). Policy `p=NONE`, disposition `NONE` |
| ARC | pass | Records the earlier results when a message is forwarded. It agrees with the three above. | `elliemcgough.me` |

**Alignment:** each check names a different part of the message:
- SPF checked the envelope sender.
- DKIM checked the `zmail` signature.
- DMARC checked the From header.

All three are `elliemcgough.me`, so both SPF and DKIM are *aligned* with From, and DMARC passes. Either one aligned pass would be enough. Passing SPF or DKIM for some other domain wouldn't pass DMARC.

## The records behind it, checked from outside

**Checked:** October 21, 2026, 17:37 UTC, with `dig @8.8.8.8` (Google's public resolver, not Cloudflare's own nameserver). The full zone listing is in [dns-https-final.md](dns-https-final.md).

| Record | Name | Value seen at 8.8.8.8 | What it does |
| --- | --- | --- | --- |
| MX | `elliemcgough.me` | `10 mx.zoho.com.`, `20 mx2.zoho.com.`, `50 mx3.zoho.com.` | Tells other mail servers where to deliver mail for `@elliemcgough.me`. The lowest number is tried first, and the others are backups. Without MX, mail to my address has nowhere to go. |
| SPF (TXT) | `elliemcgough.me` | `v=spf1 include:zohomail.com ~all` | Lists the servers allowed to send as my domain: Zoho's. `~all` asks receivers to treat anything else as suspicious (soft fail). There is exactly one SPF record, since two would fail. |
| DKIM (TXT) | `zmail._domainkey.elliemcgough.me` | `v=DKIM1; k=rsa; p=MIGfMA0G…` | The public half of the key Zoho signs my outgoing mail with. Receivers use it to check the signature. |
| DMARC (TXT) | `_dmarc.elliemcgough.me` | `v=DMARC1; p=none; rua=mailto:ellie@elliemcgough.me` | Tells receivers to check alignment. `p=none` means monitor only, don't reject. `rua` is where daily aggregate reports go. |
| Verification (TXT) | `elliemcgough.me` | `zoho-verification=zb92317202.zmverify.zoho.com` | Proved to Zoho that I control the domain. It isn't used for delivery. |

The public answers match what is stored in Cloudflare (`dns-https-final.md`). All were added on 2026-10-13. Before that, the zone had no mail records ([dns-before-zoho.md](dns-before-zoho.md)).

**Unverified:** Zoho's own "Verify all records" result wasn't saved. The passing header above shows the records work in practice.

`p=none` is deliberately loose. Tightening it to `quarantine` makes sense once the DMARC reports show only Zoho sending as the domain.
