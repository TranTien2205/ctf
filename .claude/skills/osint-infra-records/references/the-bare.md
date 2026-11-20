# On a bare box — the wire format

No dig/host/dns_query? A DNS query is a simple wire format —
a header + the question — Python socket + struct builds one;
dns_query.py is that, prebuilt. nslookup is the last resort.

## The format

- 12-byte header: ID, flags (RD set), QDCOUNT=1.
- Question: the name as length-prefixed labels + QTYPE + QCLASS.
- UDP/53 to the resolver; the answer parses the same way.
Prefer the tool to a hand-rolled query — it's the same thing.

## When to hand-roll

Almost never — dns_query.py covers the loop; a hand-rolled query only for a custom record type or a packet-level check.

## The point

The wire format exists so a bare box can still query — but dns_query.py is that, already built and tested.
