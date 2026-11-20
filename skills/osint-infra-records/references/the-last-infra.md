# The last check — infra records

Was TXT swept? Were SANs pulled (crt.sh + live cert)? Was AXFR
tried on each NS? Is every answer quoted verbatim with TTL +
resolver? Is a wildcard ruled out before counting names?

## The checks

- Every data-carrying type queried, not just A/AAAA.
- Every TXT record read, not the first.
- Every found host confirmed resolving.
- Each answer quoted with its source.

## The close

Cover the records space (sweep + whois + SANs + AXFR), confirm each lead, quote each answer — the rest is history or another class.

## Stop condition

When every answer is operational and every found host is confirmed-or-clean, the records space is done.
