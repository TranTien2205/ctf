# 403 bypasses — verbs, headers, path tricks — deep

A 403 on a real artifact is 'forbidden', not 'absent': alternate verbs, Host tricks, and path forms reopen it.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — every verb/header/path variant returns the same 403: the artifact is genuinely forbidden to this surface.

## Highest-cost traps

- X-Original-URL/X-Rewrite-URL let a proxy route you around the ACL.
- Semicolon and %2e tricks work on Java/Apache stacks.
- A 403→302 to login means auth-gated, not forbidden.

## Commands

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X OPTIONS '$BASE/.env'
curl -s -H 'X-Forwarded-For: 127.0.0.1' '$BASE/admin'
```

## Cross-references

`response-anatomy.md` · `../web-parser-differential/`
