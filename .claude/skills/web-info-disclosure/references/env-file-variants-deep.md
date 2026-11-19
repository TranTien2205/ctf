# .env variant enumeration — deep

The .env file has a family: .env.local, .env.production, .env.development, .env.bak, .env.old, .env.save, .env.example — each with different exposure rules.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — every variant returns catch-all/404: no .env exposure.

## Highest-cost traps

- Dot-file rules block .env but not .env.bak — the suffix bypasses the rule.
- The .env.example is MEANT to be safe; real values inside are the bug.
- Environment-specific files name the deployment's secrets.

## Commands

```bash
for p in /.env /.env.bak /.env.old /.env.local /.env.production /.env.example; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `static-leftovers.md`
