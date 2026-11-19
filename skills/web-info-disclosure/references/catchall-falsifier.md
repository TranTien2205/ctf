# The catch-all falsifier — the discipline

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Same byte-length body on /env and /notreal | catch-all | all 'hits' are null |
| 404 template differs from probe 200s | real discriminator | compare content |
| Random path gives real 404 while probe paths 200 | no catch-all | status is meaningful |

## Steps

1. Request a guaranteed-absent path; save the exact body.
2. Request each candidate; cmp the body bytes — not status, not length.
3. A response that differs even by a token = real content = investigate.
4. Record the catch-all signature in field notes so later probes skip it.

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.

## Traps

- Dynamic catch-alls embed the path in the body — compare on structure, not bytes.
- A baseline 404 page may itself be the catch-all for some prefixes.
- HEAD vs GET answers can differ — diff on the same verb.

## Commands

```bash
curl -s -o /tmp/baseline '$BASE/zz-no-such-9x' && for p in /.env /.git/HEAD /backup.zip; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; cmp -s /tmp/r /tmp/baseline || echo "$p DIFFERS"; done
```

## Cross-references

`response-anatomy.md` · `falsifiers.md`
