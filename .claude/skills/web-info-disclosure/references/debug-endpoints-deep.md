# Debug and actuator endpoints — deep

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Highest-cost traps

- /actuator root 404 doesn't mean /actuator/env 404s — probe specific endpoints.
- heapdump can be 100MB+ — stream and grep, don't load it.
- Some debug endpoints need a specific Accept header or auth — a 403 may be role-scoped, not closed.

## Commands

```bash
for p in /actuator /actuator/env /actuator/heapdump /__debug__/ /_profiler; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`error-pages.md` · `env-config-leaks.md` · `framework-debug.md`
