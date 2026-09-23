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
`../ctf-web/server-side-advanced.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
