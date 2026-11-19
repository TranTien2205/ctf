# Sibling .map naming conventions — deep

The .map file exists but isn't linked — found by convention: same-name.map, .min.js.map, bundle.js.map, or a maps/ directory.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no sibling maps exist under any convention: the minified bundle alone is the disclosure ceiling.

## Highest-cost traps

- Webpack/Vite/Next name maps differently — check the bundle's own path shape.
- A .map that 403s may still be fetchable under a different path form.
- Inline data-URI maps don't need a sibling file.

## Commands

```bash
curl -s -o /tmp/r -w '%{http_code}\n' '$BASE/app.js.map'
```

## Cross-references

`source-maps.md` · `tools-bundle-miner.md`
