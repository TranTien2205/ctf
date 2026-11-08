---
name: osint-infra-records
description: >
  Action-oriented depth skill for Domain, DNS and certificate records. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: osint-identity-pivot.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [osint, osint-infra-records, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Domain, DNS and certificate records

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

query TXT first because that is where a flag is actually planted, then sweep the record types that can carry data, then whois, then the certificate and its subject alternative names, which routinely leak the sibling hostname that is the real next step

**Falsifier** — the observation that closes this class: every record type returns only operational data and the certificate names no host the challenge did not already supply, so the answer is not in the live records and only an archived or transparency source could carry it
## Recognise

A domain, host, or certificate is supplied and the answer lives in records —
DNS, registration, certificates, or passive aggregators.

## Confirm

Query `TXT` first — that is where a flag is actually planted — then sweep the
record types that carry data, then `whois` and the certificate subject and its
SAN list.

| Record or source | What it can carry |
|---|---|
| `TXT` / `SPF` / `DKIM` | planted strings, verification tokens, mail policy |
| `NS`, `SOA`, `CAA` | the operators behind the zone |
| `whois` | registrar, dates, contact pattern |
| certificate transparency (`crt.sh`) | every SAN ever issued — internal names included |
| `SRV`, `MX` | service discovery, mail host names |

## Traps

- A wildcard record inflates subdomain enumeration — confirm a found name with
  a real query before counting it.
- Record answers change; note the TTL and the resolver used.
- `dig`/`host` may be absent — `tools/dns_query.py` covers the loop with
  stdlib wire-format queries; `nslookup -type=TXT` is the last fallback.

## Operational probe

```bash
python3 tools/dns_query.py --name <domain> --type TXT   # flags hide in TXT
python3 tools/dns_query.py --name <domain> --type ANY
python3 tools/dns_query.py --name <domain> --axfr --server <ns>   # zone transfer
python3 tools/dns_query.py --crtsh <domain>             # SAN leak = next hop
dig TXT <domain> +short        # or: nslookup -type=TXT <domain>
whois <domain>
```

## Routing

Shares signals with: `../osint-identity-pivot/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-osint/web-and-dns.md`
- `skills/ctf-misc/dns.md`

| Any domain/DNS/cert question | `references/dns-cert-whois.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
