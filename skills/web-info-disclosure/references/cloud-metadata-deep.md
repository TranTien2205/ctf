# Cloud metadata and internal endpoints — deep

When the app runs on a cloud host, metadata services and internal admin endpoints may be reachable directly — or via SSRF, which is a different class.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no cloud signature in headers and no internal endpoint surface: out of scope for this class.

## Highest-cost traps

- Metadata is SSRF territory when it needs a fetch primitive — route to web-ssrf.
- IMDSv2 requires a PUT token first — a simple GET failing isn't proof of absence.
- Don't scan internal ranges — the scope is the supplied target.

## Commands

```bash
curl -sI '$BASE/' | grep -iE 'x-amz|x-ms|via|server'
```

## Cross-references

`../web-ssrf/` · `header-disclosure.md`
