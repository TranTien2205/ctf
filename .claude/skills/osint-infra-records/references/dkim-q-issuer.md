# the issuer via DKIM

**Record:** DKIM — selector._domainkey — mail signing.

**Question:** the issuer — cert chain + CAA.

Query it: `python3 tools/dns_query.py --name <domain> --type DKIM`. Quote the verbatim answer.
