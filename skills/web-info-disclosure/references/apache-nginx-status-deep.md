# Apache server-status and nginx stub_status — deep

The classic /server-status (mod_status) and nginx stub_status: request lists leak other users' URLs — including tokens.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — status pages 404/403 or stripped: closed.

## Highest-cost traps

- The interesting rows are OTHER clients' requests — grep the table.
- mod_status with ExtendedStatus shows query strings — where tokens live.
- A 403 on server-status is common; try the other verbs/Host tricks.

## Commands

```bash
curl -s '$BASE/server-status' | grep -oE 'GET [^ ]+|POST [^ ]+' | sort -u | head
```

## Cross-references

`status-pages.md`
