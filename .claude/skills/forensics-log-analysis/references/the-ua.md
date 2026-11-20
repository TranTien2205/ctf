# The user-agent field — tool signatures

sqlmap, nikto, gobuster, curl/7.x, a weird custom string — the UA
distribution names the tooling; the odd UA marks the attacker's
requests.

## The signatures

- `sqlmap/1.x` — the SQLi tool
- `nikto`, `nmap`, `gobuster`, `feroxbuster` — scanners
- `curl/`, `python-requests/`, `Wget/` — scripts
- A custom or empty UA — deliberate
- `Mozilla/...` with an odd build — spoofed
The field is quoted and spaced — regex-cut it, not positional awk.
