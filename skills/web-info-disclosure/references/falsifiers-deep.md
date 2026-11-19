# Falsifiers — what closes each disclosure channel — deep

Every channel has one cheap observation that closes it. Check the falsifier before the sweep; it's cheaper.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

--

## Highest-cost traps

- A falsifier is channel-specific — .git closed doesn't close .env.
- The catch-all falsifier is the strongest: it nullifies the entire sweep at once.

## Cross-references

`catchall-falsifier.md` · `negative-results.md`
