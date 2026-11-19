# SQL dump extraction — deep

A .sql/.sql.gz/.dump file is the whole database as text — creds, hashes, and often the flag itself.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no dump file served: channel closed unless a hint names a custom dump name.

## Highest-cost traps

- Dumps can be huge — grep/stream, never open in an editor.
- Compressed dumps (.sql.gz) need gunzip before grep.
- Partial dumps still carry the most valuable tables (users).

## Commands

```bash
for p in /db.sql /dump.sql /backup.sql /database.sql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`backup-archives.md` · `env-config-leaks.md`
