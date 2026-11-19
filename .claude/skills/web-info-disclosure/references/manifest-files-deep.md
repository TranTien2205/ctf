# Dependency manifests — version disclosure to gadget recall — deep

composer.lock, package-lock.json, requirements.txt, Gemfile.lock, go.sum: pinned versions are the input to tools/gadget_lookup.py — the only version-aware recall in the tree.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no manifest is served: dependency versions must come from fingerprints in errors/headers instead.

## Highest-cost traps

- A manifest without a lockfile gives ranges, not versions — the lock is the truth.
- Dev-only deps still reveal the toolchain.
- Vendored/bundled deps won't appear in manifests — check static file paths.

## Commands

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
```

## Cross-references

`source-disclosure.md` · `secrets-in-js.md`
