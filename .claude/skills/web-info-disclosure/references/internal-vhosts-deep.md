# Internal vhosts and loopback-only routes — deep

Routes that exist only on internal hostnames or the loopback interface — disclosure finds them named in configs/comments.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no internal names exist in any leaked material: nothing to probe.

## Highest-cost traps

- Only probe names the evidence produced — don't invent vhosts.
- Loopback routes via the app's own fetch are web-ssrf, not this class.
- dev/admin vhosts often skip auth entirely.

## Commands

```bash
curl -s -H 'Host: admin.internal' '$BASE/'
```

## Cross-references

`host-header-probes.md` · `../web-ssrf/`
