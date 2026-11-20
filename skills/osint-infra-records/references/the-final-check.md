# The final check — infra records

A domain's records: TXT first, then the full sweep, whois, SANs,
AXFR. Quote each answer; a sibling host is a lead until it
resolves; all-operational is the falsifier.

## The gate

- Was TXT swept (all records)?
- Were SANs pulled (crt.sh + live cert)?
- Was AXFR tried per NS?
- Is each answer quoted with resolver + TTL?
- Is a found sibling confirmed resolving?
Then the corpus has covered the records space.

## The pass

Cover the space, confirm each lead, quote each answer — an infra-records challenge closes on the records, not a guess.
