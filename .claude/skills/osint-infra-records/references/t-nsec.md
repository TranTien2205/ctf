# NSEC walking — the hidden list

NSEC records chain every name in a signed zone — walk them to
enumerate all names without AXFR. NSEC3 hashes instead (harder).

## The walk

Query a name's NSEC — its "next" field names the next owner name;
follow the chain to enumerate the whole zone. NSEC3 hashes the
names (needs cracking), so the walk only works on NSEC zones.
