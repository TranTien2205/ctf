# The catch-all falsifier — the discipline — playbook

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Ordered playbook

1. Request a guaranteed-absent path; save the exact body.
2. Request each candidate; cmp the body bytes — not status, not length.
3. A response that differs even by a token = real content = investigate.
4. Record the catch-all signature in field notes so later probes skip it.

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.

## Commands

```bash
curl -s -o /tmp/baseline '$BASE/zz-no-such-9x' && for p in /.env /.git/HEAD /backup.zip; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; cmp -s /tmp/r /tmp/baseline || echo "$p DIFFERS"; done
```
