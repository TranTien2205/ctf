# Detection matrix — which channel is open — deep

One table: the probe, the positive answer, the file that owns it.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.

## Highest-cost traps

- Status is not the discriminator — content is.
- Each channel has its own falsifier; a closed channel doesn't close the class.

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
