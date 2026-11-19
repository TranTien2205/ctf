# Response anatomy — what each status really means

A bounded sweep is only as good as its read of each response. 200 is not 'found' and 403 is not 'absent' — content decides.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| 200 with the app's shell for every path | catch-all | content-diff, not status |
| 403 on a path that then 404s a sibling | exists-but-forbidden vs absent | verb/host tricks |
| 301/302 to a real location | route exists elsewhere | follow or note the target |
| 401 vs 403 | auth-required vs forbidden | auth class boundary |

## Steps

1. Baseline the catch-all: request a known-bogus path, save the response.
2. Diff each probe's response against the baseline — same body = no hit.
3. A 403 on a real path: try other verbs, Host/Forwarded headers, trailing slash.
4. Content-length + body hash are the discriminator when statuses lie.

## Falsifier

Falsifier — every probed path returns the identical catch-all body: nothing in the bounded list is exposed. Wider fuzzing is out of scope for this class.

## Traps

- Catch-alls often return 200 for everything — status is meaningless alone.
- A 403 that flips to 200 with a different Host header is a real finding.
- Content-length alone lies on templated pages — hash the body.

## Commands

```bash
curl -s -o /tmp/baseline '$BASE/definitely-not-real-zz9' && for p in /.env /.git/HEAD; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; cmp -s /tmp/r /tmp/baseline || echo "DIFFERS"; done
```

## Cross-references

`detection-matrix.md` · `catchall-falsifier.md`
