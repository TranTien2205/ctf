# Dependency manifests — version disclosure to gadget recall — case catalogue

composer.lock, package-lock.json, requirements.txt, Gemfile.lock, go.sum: pinned versions are the input to tools/gadget_lookup.py — the only version-aware recall in the tree.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /package.json or package-lock.json 200 | JS deps pinned | gadget_lookup --lockfile |
| 2 | /composer.lock or composer.json | PHP deps pinned | versioned gadget lookup |
| 3 | /requirements.txt or Pipfile.lock | Python deps pinned | gadget recall |
| 4 | /Gemfile.lock or go.sum | Ruby/Go deps | versioned lookup |

## Falsifier

Falsifier — no manifest is served: dependency versions must come from fingerprints in errors/headers instead.
