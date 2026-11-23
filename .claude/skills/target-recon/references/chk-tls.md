# Recon checklist: tls

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

TLS-first checklist: openssl cert harvest (subject,
issuer, SANs, dates, protocol) -> alpn negotiation ->
https intake if ALPN says http -> tls-* notes -> mtls?
record cert-required posture and stop. The cert fields
are recon facts before any HTTP.
## Pivot

Signal harvested -> out-*; route named -> that skill.
