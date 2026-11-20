# Closing — the infra-records discipline

TXT first, sweep the data types, whois, then cert+SANs. Quote the
verbatim answer with TTL+resolver; a wildcard or all-operational
set is the falsifier.

## The sequence in one line

TXT → full type sweep → whois → crt.sh SANs → AXFR → confirm each
sibling by querying it. The records are the answer or they point
at it — never stop at A/AAAA.

## The close

A records challenge closes on the verbatim record, not a guess —
sweep the types, confirm each host, quote each answer.

## The falsifier

A wildcard or an all-operational set closes the records space — then the answer is historical (crt.sh/archive/passive) or a different class.

## No flag from a pointer

A record naming a host is not the flag — read the flag from where the record points.
