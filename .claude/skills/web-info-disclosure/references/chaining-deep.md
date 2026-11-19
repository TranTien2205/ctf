# Chaining disclosure to impact — deep

A disclosed artifact is never the flag — it's the key that reaches one. Every find routes to the class that owns its sink.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — disclosed material reaches no privileged path: a finding with no chain is a hardening note, not a solve.

## Highest-cost traps

- A leaked secret that's already rotated is still evidence of the class, not impact.
- Don't stop at 'we found .env' — the chain is the point.

## Cross-references

`evidence.md` · `env-config-leaks.md`
