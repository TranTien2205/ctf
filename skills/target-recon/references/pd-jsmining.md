# Param discovery: jsmining

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

JS mining for params: fetch('/api/x?'+params),
axios({params:...}), $.get with objects, URLSearchParams,
template literals with named fields. bundle_miner emits the
endpoint inventory; param names sit in the same call sites.
Minified code still carries string param names verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
