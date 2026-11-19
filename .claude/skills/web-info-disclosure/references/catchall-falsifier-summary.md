# The catch-all falsifier — the discipline — summary

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Signal → route

- Same byte-length body on /env and /notreal → all 'hits' are null
- 404 template differs from probe 200s → compare content
- Random path gives real 404 while probe paths 200 → status is meaningful

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.
