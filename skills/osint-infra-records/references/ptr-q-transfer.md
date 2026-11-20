# a zone transfer via PTR

**Record:** PTR — reverse DNS — a hostname from an IP.

**Question:** a zone transfer — AXFR against the NS.

Query it: `python3 tools/dns_query.py --name <domain> --type PTR`. Quote the verbatim answer.
