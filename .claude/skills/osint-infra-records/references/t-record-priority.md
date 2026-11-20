# Record priority — where to look first

TXT > SANs > SRV/MX > NS/SOA > the rest — order by where the
answer actually hides, not alphabetically.

## The rationale

- TXT — where a flag is planted.
- SANs — where a sibling host leaks.
- SRV/MX — service/mail hostnames.
- NS/SOA — the operator.
- A/AAAA/CNAME — infrastructure only.
The order follows where CTF flags actually live.
