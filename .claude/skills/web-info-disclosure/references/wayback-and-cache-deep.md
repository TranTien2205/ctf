# Wayback Machine and public caches — deep

Deleted content persists: the Wayback Machine, Google cache, and archive.today hold the endpoint's history — a CTF-legitimate source when the artifact used to be public.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no snapshots or the artifact never was public: channel empty.

## Highest-cost traps

- Wayback content is historical — a found secret may be rotated; verify live.
- Some CTFs consider external archives out-of-scope — check the rules.
- The archive itself is a search: web.archive.org/web/*/url, not a probe of the target.

## Commands

```bash
curl -s 'http://archive.org/wayback/available?url=target'
```

## Cross-references

`bounded-sweep.md`
