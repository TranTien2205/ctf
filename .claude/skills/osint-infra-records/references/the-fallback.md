# When dig is absent — the fallbacks

- `dns_query.py` — the stdlib query/AXFR/crtsh/whois tool.
- `nslookup -type=TXT <domain>` — the last resort.
- Python socket + a hand-rolled query — the wire format is simple.

## The wire format in brief

A 12-byte header (id, flags, counts) + the name as length-prefixed
labels + the type + class — socket + struct builds it. dns_query.py
is that, prebuilt — prefer it to hand-rolling.

## Preference

dns_query.py over nslookup over a hand-rolled query — in that order; the first two are always available here.
