# the issuer via TXT

**Record:** TXT — planted strings, verification tokens, SPF.

**Question:** the issuer — cert chain + CAA.

Query it: `python3 tools/dns_query.py --name <domain> --type TXT`. Quote the verbatim answer.
