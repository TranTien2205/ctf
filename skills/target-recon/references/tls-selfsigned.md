# TLS recon: selfsigned

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Self-signed/internal CA: issuer == subject, or
an internal CA name (corp.local CA). Predicts: internal cert
infra, possible client-cert requirements elsewhere, hostname
mismatch tolerances. A cert naming internal.corp domains is
naming-convention recon for free.
## Pivot

Signal harvested -> out-*; route named -> that skill.
