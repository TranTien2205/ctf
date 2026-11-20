# the issuer via CNAME

**Record:** CNAME — an alias — the real host.

**Question:** the issuer — cert chain + CAA.

Query it: `python3 tools/dns_query.py --name <domain> --type CNAME`. Quote the verbatim answer.
