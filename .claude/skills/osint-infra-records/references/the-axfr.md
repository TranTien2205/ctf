# AXFR — the zone transfer

    python3 tools/dns_query.py --name <domain> --axfr --server <ns>

A misconfigured nameserver answers a full zone transfer — every
hostname in the zone at once. Try it against each listed NS.

## The sequence

1. `--type NS` → the authoritative nameservers.
2. `--axfr --server ns1` (then ns2, ...) — one may be permissive.
3. A successful transfer lists every name + record type.
4. A refusal is the norm; success is the entire zone map.

An AXFR success obviates all subdomain brute-forcing.

## Fallbacks

If every NS refuses: crt.sh SANs, a common-subdomains wordlist, NSEC walking on a signed zone — each maps names without the transfer.

## After

A transfer lists every name — grep for flag/secret/internal prefixes; each name gets its own TXT query.
