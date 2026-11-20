# TXT — the flag's home

    python3 tools/dns_query.py --name <domain> --type TXT

A planted flag, a verification token, an SPF — TXT is where the
answer lives. Sweep ALL TXT records, not the first.

## What lives in TXT

- A planted flag token — `flag{...}`.
- SPF policy — `v=spf1 ...` (can hide an include).
- Domain-verification tokens — google-site-verification etc.
- A DKIM public key at `selector._domainkey`.
- A custom planted string in any TXT record.

A domain can hold several TXT records — read every one.

## Encoding

A planted TXT may be base64, hex, or split across records — decode and concatenate before reading; the raw verbatim is still the quote.

## The order

TXT first — it is where a CTF flag is planted; sweep the rest for hosts/operators after.
