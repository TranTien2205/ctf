# a zone transfer via DKIM

**Record:** DKIM — selector._domainkey — mail signing.

**Question:** a zone transfer — AXFR against the NS.

Query it: `python3 tools/dns_query.py --name <domain> --type DKIM`. Quote the verbatim answer.
