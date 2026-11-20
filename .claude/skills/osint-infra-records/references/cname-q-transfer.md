# a zone transfer via CNAME

**Record:** CNAME — an alias — the real host.

**Question:** a zone transfer — AXFR against the NS.

Query it: `python3 tools/dns_query.py --name <domain> --type CNAME`. Quote the verbatim answer.
