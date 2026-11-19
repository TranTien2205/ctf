# The catch-all falsifier — the discipline — case catalogue

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Same byte-length body on /env and /notreal | catch-all | all 'hits' are null |
| 2 | 404 template differs from probe 200s | real discriminator | compare content |
| 3 | Random path gives real 404 while probe paths 200 | no catch-all | status is meaningful |

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.

## Coverage notes

- Dynamic catch-alls embed the path in the body — compare on structure, not bytes.
- A baseline 404 page may itself be the catch-all for some prefixes.
- HEAD vs GET answers can differ — diff on the same verb.

## Cross-references

`response-anatomy.md` · `falsifiers.md`
