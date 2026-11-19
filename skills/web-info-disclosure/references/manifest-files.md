# Dependency manifests — version disclosure to gadget recall

composer.lock, package-lock.json, requirements.txt, Gemfile.lock, go.sum: pinned versions are the input to tools/gadget_lookup.py — the only version-aware recall in the tree.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /package.json or package-lock.json 200 | JS deps pinned | gadget_lookup --lockfile |
| /composer.lock or composer.json | PHP deps pinned | versioned gadget lookup |
| /requirements.txt or Pipfile.lock | Python deps pinned | gadget recall |
| /Gemfile.lock or go.sum | Ruby/Go deps | versioned lookup |

## Steps

1. Fetch the manifest (and lockfile where it exists — locks carry exact versions).
2. python3 tools/gadget_lookup.py --lockfile <path>/package-lock.json — has this dependency been measured here?
3. A pinned vulnerable version routes to the owning bug-class skill, not 'exploit the CVE blind'.
4. Note the versions in field-notes for the chain.

## Falsifier

Falsifier — no manifest is served: dependency versions must come from fingerprints in errors/headers instead.

## Traps

- A manifest without a lockfile gives ranges, not versions — the lock is the truth.
- Dev-only deps still reveal the toolchain.
- Vendored/bundled deps won't appear in manifests — check static file paths.

## Commands

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
```

## Cross-references

`source-disclosure.md` · `secrets-in-js.md`
