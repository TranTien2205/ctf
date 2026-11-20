# dns_query.py — the local route

    python3 tools/dns_query.py --name <d> --type TXT
    python3 tools/dns_query.py --name <d> --type ANY
    python3 tools/dns_query.py --name <d> --axfr --server <ns>
    python3 tools/dns_query.py --crtsh <d>
    python3 tools/dns_query.py --whois <d>

Stdlib wire-format queries — works without dig/host/nslookup.

## The subcommands

- `--name <d> --type TXT|ANY|MX|NS|SOA|CAA|SRV|PTR|A|AAAA|CNAME`
- `--axfr --server <ns>` — zone-transfer attempt.
- `--crtsh <d>` — the SAN list.
- `--whois <d>` — TCP/43 registration.
One tool covers the whole loop with no external binaries.

## Order

TXT → ANY → crtsh → whois → axfr per NS — the coverage order the tool supports in one pass.
