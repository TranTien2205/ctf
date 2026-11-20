# the issuer via PTR

**Record:** PTR — reverse DNS — a hostname from an IP.

**Question:** the issuer — cert chain + CAA.

Query it: `python3 tools/dns_query.py --name <domain> --type PTR`. Quote the verbatim answer.
