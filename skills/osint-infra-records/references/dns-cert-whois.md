# DNS, certificate, and whois records

Infrastructure records are public by design — the skill is knowing which
record answers which question, and reading them in the order that builds
the map.

## The record types and what they answer

| Question | Record |
|---|---|
| Where is it hosted? | `A`/`AAAA` → the IP; `whois <ip>` → the AS/org |
| What else lives here? | `NS` (nameservers), reverse DNS on the IP, `crt.sh` on the domain |
| What subdomains exist? | `crt.sh` SAN list, `subfinder`/`amass`, `host` on guesses |
| What's the mail config? | `MX`, `TXT` (SPF/DKIM/DMARC leak internal relays) |
| What services run? | `SRV`, `TXT`, CNAMEs pointing at SaaS (Heroku, S3, GitHub Pages) |
| Who registered it? | `whois` — usually privacy-protected now; historical whois (DomainTools) may not be |
| When was it made? | `whois` creation date + `crt.sh` first-seen — bounds the campaign |
| What certificates exist? | `crt.sh`, `censys.io` — every SAN is a subdomain or internal name |

## The working order

```bash
whois target.com
dig +short A target.com ; dig +short NS target.com ; dig +short MX target.com
dig +short TXT target.com
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u
```

`crt.sh` output is the single highest-yield record — one query returns every
subdomain that ever held a cert, including internal names never meant to be
public.

## What leaks what

| Leaked | Leads to |
|---|---|
| a CNAME to `*.github.io`, `*.herokuapp.com` | the service behind it — often takeover-able if unclaimed |
| `TXT` with `v=spf1 include:` | the mail providers — internal relay names |
| a SAN `internal.corp.com` on a public cert | an internal hostname to try via SSRF/Host games |
| nameserver `ns1.cloudprovider.com` | the provider — and the attack surface that goes with it |
| old `A` record in Wayback | the previous host — sometimes still answering |

## Falsifier

The domain answers only the expected records — one A, one NS pair, no SANs
beyond the domain itself, privacy-protected whois with no history. The infra
is minimal; the flag is in a different layer.

## Traps

- `crt.sh` includes expired and never-deployed certs — a listed subdomain
  may not resolve; always `dig` before treating it as real.
- `whois` is rate-limited and increasingly empty; use it for dates, not for
  the registrant name.
- Wildcard DNS (`*.target.com -> same IP`) makes every guess "resolve" —
  confirm a found subdomain actually serves distinct content.
- Round-robin `A` records mean one IP isn't the host — collect all of them.
