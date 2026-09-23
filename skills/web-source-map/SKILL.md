---
name: web-source-map
description: >
  Front-end bundle and source-map recon. Use when the app ships a JavaScript
  bundle (React, Vue, Next.js, webpack, Vite) and the front-end is the only
  source available. Recover original sources, endpoints, feature flags and
  secrets from bundles and .map files.
tags: [web, javascript, source-map, recon, ctf]
environment: [ctf, lab, authorized-testing]
---

# Front-end bundle and source-map recon

**Catalogue technique.** Nothing in this toolkit has solved a challenge with this
technique yet. Treat it as standard published knowledge and record real results
in `field-notes.md`.

## Recognise

A single-page app, `/_next/static/`, `/static/js/`, `/assets/index-*.js`, a
`//# sourceMappingURL=` comment, or a `*.js.map` reference. The front-end is
source too: it names every endpoint, parameter and sometimes a key.

## Operational probe

1. Fetch the entry page and list every script URL it loads.
2. Fetch each bundle and extract: URLs, route paths, parameter names, feature
   flags, `api/` prefixes, and any string that looks like a key or token.
3. Request the bundle's `.map` file (`<bundle>.js.map`) and, for Next.js, the
   `_buildManifest.js` and `_ssgManifest.js`.

```bash
curl -s "$BASE/" | grep -oE '/[A-Za-z0-9._/-]+\.js' | sort -u
curl -s "$BASE/static/js/main.js" | grep -oE '"/[A-Za-z0-9_./?=&-]+"' | sort -u
curl -s -o map.json -w '%{http_code}\n' "$BASE/static/js/main.js.map"
```

Expected confirmation is an endpoint, parameter, secret, or original source that
the rendered page did not expose. A minified bundle with no readable strings and
a 404 map is a falsifier for this route.

## What to do with it

- Every endpoint found is a real endpoint: feed it to `../web-triage/` rather
  than directory brute force.
- A leaked key or token goes to `../web-auth-session/`.
- A hidden admin route goes to `../web-idor/` or `../web-logic-flaw/`.
- A `sourceMappingURL` that resolves means original source, not just minified
  code; read the real file names and logic.

## Traps

- A 200 with HTML for a `.map` request is a catch-all, not a source map; check
  the content type and the first bytes.
- Next.js chunks are per-route; the interesting endpoint is often in a page
  chunk, not `main`.
- Do not open the whole bundle into context; grep for the specific token.

## Routing

Shares signals with: `../web-triage/`, `../file-read-primitives/`. Depth, one
named file at a time: `../ctf-web/client-side.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
