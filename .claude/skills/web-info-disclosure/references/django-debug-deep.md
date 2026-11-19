# Django DEBUG=True — the yellow page — deep

Django's debug error page dumps settings values, the SQL query, request vars, and the full Python traceback — a multi-layer disclosure.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — generic 404/500 pages only: DEBUG is off.

## Highest-cost traps

- DEBUG pages show settings VALUES — including keys Django would mask elsewhere.
- The local vars in each traceback frame carry more secrets than the settings block.
- A DEBUG=False app still leaks via custom error handlers.

## Commands

```bash
curl -s '$BASE/nonexistent-path' | grep -i django
```

## Cross-references

`framework-debug.md` · `error-pages.md`
