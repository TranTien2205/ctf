# The checklist

- [ ] TXT swept (all records)
- [ ] Data types swept: SPF/DKIM/SRV/MX/NS/SOA/CAA/ANY
- [ ] whois — registrar + dates + pattern
- [ ] crt.sh — SAN siblings
- [ ] AXFR attempted on each NS
- [ ] Wildcard ruled out before counting names
- [ ] TTL + resolver noted
- [ ] Verbatim answers quoted
- [ ] A found sibling's own records queried
- [ ] A record chain (CNAME/MX) followed to its end
- [ ] crt.sh history checked when live is clean
- [ ] All-operational recorded as the falsifier if so
- [ ] A found host's own SANs pulled (recursion)
- [ ] The authoritative NS queried for current truth

## The close

All types swept + whois + SANs + AXFR + siblings confirmed + answers quoted — then the records space is covered; anything left is history (crt.sh/archive/passive).

- [ ] A second source corroborated a found host
- [ ] The record-vs-web handoff decided

- [ ] A hand-rolled or absent tool never claimed
- [ ] A lead distinguished from a measured answer

- [ ] Planted vs operational TXT distinguished
- [ ] A flag-shaped string read verbatim, not inferred
