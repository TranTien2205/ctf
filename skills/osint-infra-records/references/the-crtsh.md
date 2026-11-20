# crt.sh — certificate transparency

    python3 tools/dns_query.py --crtsh <domain>

Every cert logged for the domain — the SAN list leaks internal
hostnames; a subdomain sweep without brute-forcing.

## The endpoint

`https://crt.sh/?q=%25.<domain>&output=json` — every logged cert.
Dedup the `name_value` fields (a cert may list many SANs) and
sort out internal/staging/dev names — those are the candidates.
Also `crt.sh/?q=<domain>` for the HTML view.

## Dedup

The same SAN appears across many certs — dedup name_value entries, sort internal/staging/dev to the top.
