# Evasion (deep) — the bundle's resistance and the deployment's gaps

## Note: this is recon, not payload evasion

There is no WAF in the fetch — the resistance is the *bundle's* to being
read, and the "evasion" is working around obfuscation and finding the
richer artifact the deployment left.

## Working around obfuscation

| Resistance | Workaround |
|---|---|
| string-array obfuscation | extract/decode the packed array; or grep for the shape |
| control-flow flattening | skip the flow; grep the literals |
| encoded strings (`atob`/`\x`/`\u`) | decode the escapes; grep for the decoded shape |
| identifier mangling | irrelevant to strings — endpoints/keys survive |
| dead-code + indirection | `strings` + shape-grep; a deobfuscator last |
| a heavy obfuscator | `webcrack`/`unminify`/manual array decode |

The obfuscator cannot remove the strings the runtime needs — it can only
move and encode them. Grep for the *shape* (`/api/`, `token`, `flag{`,
`http`) always surfaces what logic-hiding could not.

## The no-map fallback

Production disables sourcemaps — the common case, not a blocker.
String mining yields endpoints/params/flags/secrets regardless. The map
is a bonus, not a requirement.

## The dev-build leak — the bigger yield

A `?env=dev`, `.dev`/staging host, `main.dev.js`, a `webpackHotDevClient`
marker — the dev build ships sourcemaps on, debug flags, dev endpoints,
`console.log` secrets. Probe for a dev bundle/host — it is a
higher-yield target than the prod bundle.

```bash
# dev/staging surface probes
curl -s "$BASE/?env=dev" "$BASE/main.dev.js.map" -o /dev/null -w '%{http_code}\n'
curl -s "https://dev.$HOST/" -o /dev/null -w '%{http_code}\n'
grep -oE 'webpackHotDevClient|module\.hot|webpack-dev-server|sourceURL=' bundle.js
```

## The authenticated bundle

A session-gated app serves the bundle to logged-in users — `bundle_miner
-H "Cookie: $C"`. The authenticated bundle is a richer surface: the
routes, endpoints, and config a guest cannot see.

## The adjacent-disclosure pivot

A deployment lax enough to ship `.map` ships more — `.git`, `.env`,
backups, `src/`, `static/maps/`, `asset-manifest.json`. The map is the
signal; the adjacent surface is the bigger leak. See
`adjacent-disclosure.md`.

## The per-environment config

`config.dev.js` vs `config.prod.js`, `env.js?env=dev` — a per-environment
config may carry dev keys, debug flags, internal endpoints the prod
config hides.

## The source-path-served case

The map's `sources` paths may be hosted directly — `/src/config/x.js`,
`/static/src/api/y.js`. Probe the source paths on the host; a served
source file is the map without the map.
