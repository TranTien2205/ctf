# Response anatomy — what each status really means — deep

A bounded sweep is only as good as its read of each response. 200 is not 'found' and 403 is not 'absent' — content decides.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — every probed path returns the identical catch-all body: nothing in the bounded list is exposed. Wider fuzzing is out of scope for this class.

## Highest-cost traps

- Catch-alls often return 200 for everything — status is meaningless alone.
- A 403 that flips to 200 with a different Host header is a real finding.
- Content-length alone lies on templated pages — hash the body.

## Commands

```bash
curl -s -o /tmp/baseline '$BASE/definitely-not-real-zz9' && for p in /.env /.git/HEAD; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; cmp -s /tmp/r /tmp/baseline || echo "DIFFERS"; done
```

## Cross-references

`detection-matrix.md` · `catchall-falsifier.md`
