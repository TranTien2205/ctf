# Dependency manifests — version disclosure to gadget recall — checklist

composer.lock, package-lock.json, requirements.txt, Gemfile.lock, go.sum: pinned versions are the input to tools/gadget_lookup.py — the only version-aware recall in the tree.

## Checklist

- [ ] Fetch the manifest (and lockfile where it exists — locks carry exact versions).
- [ ] python3 tools/gadget_lookup.py --lockfile <path>/package-lock.json — has this dependency been measured here?
- [ ] A pinned vulnerable version routes to the owning bug-class skill, not 'exploit the CVE blind'.
- [ ] Note the versions in field-notes for the chain.

## Abort conditions

- A manifest without a lockfile gives ranges, not versions — the lock is the truth.
- Dev-only deps still reveal the toolchain.
- Vendored/bundled deps won't appear in manifests — check static file paths.

## Falsifier

Falsifier — no manifest is served: dependency versions must come from fingerprints in errors/headers instead.
