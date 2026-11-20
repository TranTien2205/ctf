# Query syntax across tools

- dig: `dig TYPE name @server` + `+short` for terse.
- host: `host -t TYPE name server`.
- nslookup: `nslookup -type=TYPE name server`.
- dns_query.py: `--name name --type TYPE`.
Equivalent answers; dns_query works with no dig.

## Choosing the tool

- dig/host — the canonical output + server control.
- dns_query.py — the local stdlib; covers TXT/AXFR/crtsh/whois.
- nslookup — the bare-box fallback.
Use whichever is present; dns_query.py is always available here.
