# crt.sh — the JSON endpoint

`https://crt.sh/?q=%25.domain&output=json` — every logged cert's
name_value list. Dedup the SANs; internal/staging/dev names stand
out. dns_query.py --crtsh wraps it.

## The fields

- `name_value` — the SAN list (one per line, may repeat).
- `not_before`/`not_after` — the cert's window.
- `issuer_name` — the CA.
Dedup the SANs and sort internal/staging/dev names to the top.
