# Two sources — corroborate

A found hostname (a SAN, an NS, an MX) is corroborated by a second
source — a passive-DNS entry, an archive capture, or the live host
itself. Two agreeing sources beat one.

## The sources

- The live DNS answer.
- crt.sh / certificate transparency.
- Passive DNS history.
- The live host's own cert/banner.
A name in one source confirmed by another is solid.

## Minimum

One source is a hint; two agreeing sources is the answer. For a host: a SAN plus its own resolution.
