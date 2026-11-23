# Probe: tools/web/http_probe.py

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

The sanctioned request: it holds request+response
together and emits the post-probe command - use it
for every recon observation that may feed hooks.

## Pivot

Signal harvested -> out-*; route named -> that skill.
