# the issuer via SOA

**Record:** SOA — zone serial + responsible party.

**Question:** the issuer — cert chain + CAA.

Query it: `python3 tools/dns_query.py --name <domain> --type SOA`. Quote the verbatim answer.
