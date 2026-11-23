# CDN/WAF identity: fastly

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Fastly identity: x-served-by (cache node codes),
x-cache/x-cache-hits, fastly-* headers, Via: varnish.
Predicts: VCL cache-key manipulation surface, surrogate-key
cache tagging, stale-while-revalidate behavior = cache
deception/poisoning class notes.
## Pivot

Signal harvested -> out-*; route named -> that skill.
