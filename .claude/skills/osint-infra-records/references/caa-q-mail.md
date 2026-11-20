# mail setup via CAA

**Record:** CAA — which CAs may issue — the operators.

**Question:** mail setup — MX, SPF, DKIM, DMARC.

Query it: `python3 tools/dns_query.py --name <domain> --type CAA`. Quote the verbatim answer.
