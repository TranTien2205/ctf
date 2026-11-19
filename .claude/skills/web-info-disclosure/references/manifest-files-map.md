# Dependency manifests — version disclosure to gadget recall — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /package.json or package-lock.json 200 | JS deps pinned | gadget_lookup --lockfile |
| /composer.lock or composer.json | PHP deps pinned | versioned gadget lookup |
| /requirements.txt or Pipfile.lock | Python deps pinned | gadget recall |
| /Gemfile.lock or go.sum | Ruby/Go deps | versioned lookup |

## Falsifier

Falsifier — no manifest is served: dependency versions must come from fingerprints in errors/headers instead.
