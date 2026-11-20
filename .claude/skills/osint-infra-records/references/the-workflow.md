# The infra-records workflow — TXT first

A domain/host/cert is supplied; the answer lives in DNS,
registration, certificates, or passive aggregators.

## The order

1. TXT first — where a flag is actually planted.
2. Sweep the data-carrying types — SPF/DKIM/SRV/MX/NS/SOA/CAA/ANY.
3. whois — registrar, dates, contact pattern.
4. The cert + its SANs — the sibling hostname that is the next step.
5. crt.sh — every SAN ever issued, internal names included.
6. AXFR attempt — a permissive NS spills the whole zone.

Quote the verbatim answer; note the TTL and the resolver.

## The reasoning

TXT is where a flag is actually planted — not a step, the answer.
The SAN list leaks sibling hostnames the challenge never supplied.
AXFR dumps the whole zone when a nameserver is permissive. Order
by where the answer hides, not alphabetically.

## After a lead

A SAN or record names a host → query ITS records (TXT/A/SANs) →
the sibling's own surface opens. Each found host repeats the
loop until the records are all operational or the flag appears.

## When it's all operational

Then the answer isn't in the live records — pivot to crt.sh
history, archive.org snapshots, or passive DNS for what the
records once held; or reclassify to the class the question
actually names.

## The loop

records → found host → its records → next host — recurse until every answer is operational or the flag appears.

## The principle

Every record type can carry the answer; order by where it hides (TXT, SANs, SRV/MX, NS/SOA), not alphabetically.
