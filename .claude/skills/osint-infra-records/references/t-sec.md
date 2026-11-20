# DNSSEC — the signed zone

DNSSEC RRSIG/DNSKEY records prove a signed zone; a zone walk via
NSEC records (not NSEC3) enumerates every name — an AXFR
alternative when NSEC is used.

## Reading it

- DNSKEY + RRSIG = a signed zone.
- NSEC = a walkable name chain.
- NSEC3 = hashed names — needs cracking.
A signed zone leaks its names via NSEC without needing AXFR.
