# The traps

- Wildcard inflation — confirm a found name with a real query.
- Stale/cached answers — note TTL + resolver.
- Claiming a dig/host result when the tool is absent — dns_query.py.
- Stopping at A/AAAA — TXT/SRV/SANs carry the answer.
- Reading only the first TXT when several exist.
- A CNAME's alias treated as the final answer — follow it.
- ANY refused by many resolvers — sweep the types explicitly.
- Treating a found hostname as a confirmed host before it resolves.
- Ignoring the TTL — a stale cached answer misleads.
- Confusing a CTF-planted TXT with a real SPF token.

## More traps

- A parked/forwarding domain returns a generic answer.
- An internationalized name (punycode) confuses a query.
- A CNAME chain ending at a CDN names the CDN, not a sibling.

- An expired cert still names a SAN that once existed.
- A round-robin A returns different IPs — note all of them.

- A registrar-parked domain returns parked records — note it.
