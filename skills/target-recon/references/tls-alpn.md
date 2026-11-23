# TLS recon: alpn

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ALPN negotiation: openssl s_client -alpn h2,http/1.1
- negotiated protocol names HTTP/2 vs 1.1 support = smuggling/
protocol class notes. h3/QUAD hint via Alt-Svc header.
Record the negotiated proto verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
