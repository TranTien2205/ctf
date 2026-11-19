# The catch-all falsifier — the discipline — deep

The class's defining falsifier: a SPA fallback or wildcard route returns the same 200+HTML for every path. Without a baseline diff, every probe 'finds' the same fake hit.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — every probed path byte-matches the absent-path baseline: nothing was disclosed; the whole sweep is negative.

## Highest-cost traps

- Dynamic catch-alls embed the path in the body — compare on structure, not bytes.
- A baseline 404 page may itself be the catch-all for some prefixes.
- HEAD vs GET answers can differ — diff on the same verb.

## Commands

```bash
curl -s -o /tmp/baseline '$BASE/zz-no-such-9x' && for p in /.env /.git/HEAD /backup.zip; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; cmp -s /tmp/r /tmp/baseline || echo "$p DIFFERS"; done
```

## Cross-references

`response-anatomy.md` · `falsifiers.md`
