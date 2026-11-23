# Recon negative: cdnuniform

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Negative: CDN-uniform responses. Every path
200s or every path serves the same shell = edge behavior,
not app content - baseline-compare to find REAL endpoints
(cache-key differences, x-cache miss on real routes). The
uniform response is the negative to record.
## Pivot

Signal harvested -> out-*; route named -> that skill.
