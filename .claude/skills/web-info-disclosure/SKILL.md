---
name: web-info-disclosure
description: >
  Information disclosure and exposed-artifact testing. Use when the flag or the
  next step may sit in an exposed file or endpoint: .git, .env, backups, source
  archives, debug or actuator routes, verbose errors, or an unlinked static path.
tags: [web, info-disclosure, recon, source-leak, ctf]
environment: [ctf, lab, authorized-testing]
---

# Information disclosure

**Catalogue technique.** Nothing in this toolkit has solved a challenge by
disclosure alone yet. Treat it as standard published knowledge and record real
results in `field-notes.md`.

## Recognise

The bug you need is not always a sink; sometimes the answer is already served.
Signals: a 403 with a stack trace, a debug header, a `Server-Timing` full of
framework detail, a `X-Powered-By`, a referenced but unlinked asset, or a
challenge that ships a `.git` directory or an archive.

## Operational probe

Test a **small, bounded** list of well-known paths and read the response, rather
than running a wide scanner blindly:

```bash
for p in /.git/HEAD /.env /.env.bak /backup.zip /app.zip /www.zip \
         /robots.txt /sitemap.xml /.DS_Store /server-status \
         /actuator /actuator/env /debug /api/swagger.json; do
  code=$(curl -s -o /tmp/r -w '%{http_code}' --max-time 8 "$BASE$p")
  echo "$p $code $(wc -c </tmp/r)"
done
```

For a `.git` that is served, reconstruct the repository rather than reading one
file:

```bash
git clone --no-checkout "$BASE/.git" repo 2>/dev/null && cd repo && git checkout -- .
```

If the clone fails — no git on the box, or the server does not speak the
smart protocol — walk the loose objects over plain HTTP instead:

```bash
python3 tools/web/git_dumper.py --base "$BASE/.git/" --out repo
```

It resolves `HEAD`, walks commit -> tree -> blob, inflates each loose
object and writes the working tree out. A pack-only repository is
reported honestly rather than half-parsed.

Expected confirmation is a real artifact — source, config, key, commit history,
or the flag — not a catch-all 200. A generic 200 with the app's HTML for every
path is a falsifier; check the content, not the status.

## Where it usually is

- Version control: `/.git/`, `/.svn/`, `/.hg/`.
- Config and secrets: `/.env`, `/config.json`, `/credentials.yml.enc`.
- Archives and backups: `/backup.zip`, `/app.tar.gz`, `/<name>.sql`.
- Framework debug: `/actuator/*`, `/debug`, `__debug__`, verbose error pages.
- Static leftovers: `.map`, `.bak`, `~`, `.swp`, `/.DS_Store`.
- Error pages that echo a path, query, or environment value.

## Traps

- Do not port-scan or directory-brute-force a shared host; use the observed
  surface and a bounded path list.
- Redact any credential or key found; do not write it into the repository.
- A 403 for `/.git/config` can still mean `/.git/HEAD` is readable; check the
  specific files.
- A disclosure is a means, not the goal: chain it (source to sink, key to
  session, path to traversal) before claiming impact.

## Routing

Shares signals with: `../file-read-primitives/`, `../web-auth-session/`,
`../web-source-map/`. Depth, one named file at a time:

| Question | File |
|---|---|
| The ordered pass | `references/workflow.md` `references/recon-order.md` `references/bounded-sweep.md` |
| The catch-all baseline — before anything | `references/catchall-falsifier.md` `references/response-anatomy.md` |
| Which channel is open | `references/detection-matrix.md` `references/per-signal.md` `references/per-path.md` |
| .git / VCS | `references/git-exposure.md` `references/version-control-metadata.md` `references/tools-git-dumper.md` |
| Config / secrets / keys | `references/env-config-leaks.md` `references/env-file-variants.md` `references/pem-key-files.md` `references/secrets-in-js.md` |
| Archives / dumps / manifests | `references/backup-archives.md` `references/sql-dump-read.md` `references/manifest-files.md` `references/static-config-files.md` `references/ide-and-ci-files.md` |
| Source / leftovers / maps | `references/source-disclosure.md` `references/static-leftovers.md` `references/swp-and-temp.md` `references/ds-store-parse.md` `references/source-maps.md` `references/sourcemap-sibling.md` |
| Debug / errors / ops surfaces | `references/debug-endpoints.md` `references/error-pages.md` `references/framework-debug.md` `references/spring-actuator-deep.md` `references/django-debug.md` `references/laravel-debug.md` `references/werkzeug-debug.md` `references/phpinfo-read.md` `references/status-pages.md` `references/apache-nginx-status.md` `references/prometheus-metrics.md` `references/health-endpoints.md` `references/log-exposure.md` |
| Route discovery | `references/robots-sitemap.md` `references/api-docs-exposure.md` `references/graphql-introspection.md` `references/oauth-wellknown.md` `references/redirect-leaks.md` `references/comment-leaks.md` `references/internal-vhosts.md` `references/header-disclosure.md` `references/header-leaks-deep.md` `references/well-known-and-meta.md` `references/cloud-metadata.md` `references/wayback-and-cache.md` `references/graphql-and-ws-endpoints.md` |
| A 403 on something real | `references/alternate-verbs.md` `references/host-header-probes.md` `references/error-timing.md` |
| Chain the find | `references/chaining.md` `references/multi-step-chains.md` |
| Tools | `references/tools-git-dumper.md` `references/tools-bundle-miner.md` `references/tools-http-probe.md` `references/tools-read-loop.md` `references/tools-id-sweep.md` |
| Discipline | `references/evidence.md` `references/falsifiers.md` `references/preconditions.md` `references/negative-results.md` `references/anti-patterns.md` `references/boundary-cases.md` `references/troubleshoot.md` `references/operator-notes.md` `references/glossary.md` `references/field-manual.md` `references/worked-examples.md` `references/case-studies.md` `references/closing-index.md` |

`../ctf-web/server-side-advanced.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
