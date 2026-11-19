# Error pages — stack traces and verbose errors — deep

Verbose errors leak file paths, framework versions, query strings, line numbers, and sometimes code context. Trigger them deliberately with malformed input.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — all error paths return a generic branded error page with no internals: verbose errors are off. The channel is closed.

## Highest-cost traps

- A 500 with a generic page is not disclosure — you need internals in the body.
- Error pages behind a CDN may be normalized; try direct-host probes if given.
- Don't confuse 'page not found' styling with framework internals.

## Commands

```bash
curl -s 'https://t/?id=abc' ; curl -s -X POST -H 'Content-Type: application/json' -d '{bad' 'https://t/api'
```

## Cross-references

`detection-matrix.md` · `debug-endpoints.md` · `header-disclosure.md`
