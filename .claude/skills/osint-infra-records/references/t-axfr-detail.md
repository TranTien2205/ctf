# AXFR — trying each NS

Get NS records, then `--axfr --server <each>` — a permissive
nameserver dumps the whole zone (every name + record). Refusal is
normal; success is a full subdomain map.

## The technique

AXFR runs over TCP/53 — a permissive NS returns the zone serial
then every RRset. Try each authoritative NS; a single permissive
one spills the whole list of hostnames.
