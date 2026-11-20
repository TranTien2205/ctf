# The record sweep — every data type

    for t in TXT SPF DKIM SRV MX NS SOA CAA PTR A AAAA CNAME; do
        python3 tools/dns_query.py --name <d> --type $t; done

Each type can carry the answer — don't stop at A/AAAA.

## What each can hold

- TXT/SPF — the flag, tokens, mail policy.
- DKIM/DMARC — mail signing + a planted selector.
- MX — a mail host (sibling).
- NS/SOA — the operator.
- SRV — named services.
- CNAME — an alias to follow.
- PTR — a hostname from an IP.

## The order

TXT first (the flag), then SPF/DKIM/DMARC (mail), MX/SRV (hosts), NS/SOA/CAA (operator), PTR (reverse) — by where the answer hides.
