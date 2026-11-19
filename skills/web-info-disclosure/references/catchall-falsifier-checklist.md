# The catch-all falsifier — the discipline — operational checklist

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Checklist

- [ ] Request a guaranteed-absent path; save the exact body.
- [ ] Request each candidate; cmp the body bytes — not status, not length.
- [ ] A response that differs even by a token = real content = investigate.
- [ ] Record the catch-all signature in field notes so later probes skip it.

## Abort conditions

- Dynamic catch-alls embed the path in the body — compare on structure, not bytes.
- A baseline 404 page may itself be the catch-all for some prefixes.
- HEAD vs GET answers can differ — diff on the same verb.

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.

## Cross-references

`response-anatomy.md` · `falsifiers.md`
