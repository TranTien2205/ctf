# Workflow — the ordered disclosure pass

## Phase 1: baseline (2 requests)

- Baseline the catch-all: a guaranteed-absent path → save the body.
- Header read: `curl -sI` the base URL — fingerprint + topology.

## Phase 2: canonical sweep (~15 paths)

/.git/HEAD /.env /robots.txt /sitemap.xml /backup.zip /actuator
/server-status /.DS_Store /phpinfo.php /swagger.json /.well-known/

Read bodies, not statuses. Diff every 200 against the baseline.

## Phase 3: route each hit

| Hit | File |
|---|---|
| 'ref:' in HEAD | `git-exposure.md` |
| KEY=VALUE body | `env-config-leaks.md` |
| archive magic | `backup-archives.md` |
| actuator JSON | `debug-endpoints.md` |
| index page | `directory-listing.md` |
| spec JSON | `api-docs-exposure.md` |
| binary .DS_Store | `ds-store-parse.md` |

## Phase 4: targeted follow-ups

- 403s → `alternate-verbs.md` (verbs, Host, path tricks).
- Framework fingerprint → `framework-debug.md` family paths.
- Found filenames → targeted probes (never invented names).

## Phase 5: chain

- Each find → `chaining.md` → the owning class.

## Stop

- Catch-all falsifier fires on everything → recorded negative, done.
- A find chains to impact → continue in the owning class.
