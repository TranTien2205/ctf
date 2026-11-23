# Header depth: securityposture

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Security-header posture inventory: CSP
(present? nonce? wildcard?), X-Frame-Options, HSTS (max-age,
preload), X-Content-Type-Options, Referrer-Policy, Permissions-
Policy. Absent headers are posture observations; a CSP
verbatim feeds the xss class's bypass picture.
## Pivot

Signal harvested -> out-*; route named -> that skill.
