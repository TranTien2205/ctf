# Response anatomy — what each status really means — case catalogue

A bounded sweep is only as good as its read of each response. 200 is not 'found' and 403 is not 'absent' — content decides.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | 200 with the app's shell for every path | catch-all | content-diff, not status |
| 2 | 403 on a path that then 404s a sibling | exists-but-forbidden vs absent | verb/host tricks |
| 3 | 301/302 to a real location | route exists elsewhere | follow or note the target |
| 4 | 401 vs 403 | auth-required vs forbidden | auth class boundary |

## Falsifier

Falsifier — every probed path returns the identical catch-all body: nothing in the bounded list is exposed. Wider fuzzing is out of scope for this class.

## Coverage notes

- Catch-alls often return 200 for everything — status is meaningless alone.
- A 403 that flips to 200 with a different Host header is a real finding.
- Content-length alone lies on templated pages — hash the body.

## Cross-references

`detection-matrix.md` · `catchall-falsifier.md`
