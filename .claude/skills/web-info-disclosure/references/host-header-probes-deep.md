# Host and forwarded-header probing — deep

The app's trust in Host/X-Forwarded-Host splits internal vs external views — some artifacts only serve to the internal name.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — every Host variant returns the same content: single vhost, nothing hidden behind routing.

## Highest-cost traps

- Don't invent hostnames — use names leaked by certs, comments, headers.
- This boundary is shared with web-host-header — deeper attacks live there.
- A 403→200 flip under Host: localhost is a real misconfig.

## Commands

```bash
curl -s -H 'Host: localhost' '$BASE/admin' ; curl -s -H 'X-Forwarded-Host: 127.0.0.1' '$BASE/.env'
```

## Cross-references

`../web-host-header/` · `alternate-verbs.md`
