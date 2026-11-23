# Recon negative: wafblock

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Negative: WAF blocks recon itself. Status/page
shape records the block (cdn-* fingerprints it); the allowed-
method set via OPTIONS and neutral probes still works.
Enumerate what the WAF permits; the block event is the
observation.
## Pivot

Signal harvested -> out-*; route named -> that skill.
