# Spring Actuator — the full endpoint map — deep

Actuator's value isn't /env alone — it's the whole endpoint inventory: mappings, beans, configprops, heapdump, sessions.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — only health/info exposed and they're minimal: the rich endpoints are off.

## Highest-cost traps

- Actuator paths differ between Boot 2/3 and configs — enumerate from the root.
- heapdump needs analysis tooling (strings + grep is enough for secrets).
- Some endpoints are write-capable (shutdown, restart) — read-only is the disclosure boundary.

## Commands

```bash
curl -s '$BASE/actuator' ; curl -s '$BASE/actuator/env'
```

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
