# Recon trap: httpsonly

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Trap: http-only recon on an https target. The
HTTP port redirecting to 443 is not a finding - follow one
redirect hop within the same host/port family and record the
scheme map; a cross-host redirect is scope, not surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
