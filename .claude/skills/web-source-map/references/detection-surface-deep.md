# Detection surface (deep) — every file and region that carries signal

## The asset files

| File | Carries | Priority |
|---|---|---|
| entry page (`/`) | `<script src>` list, `__NEXT_DATA__`, SPA root | the inventory |
| `main.[hash].js` | the app shell, route table, config | high |
| `[n].chunk.js` / page chunks | per-route logic, hidden endpoints | high |
| `app.[hash].js` (Vue) | the app + routes | high |
| `index-[hash].js` (Vite) | the ESM entry | high |
| `[n].[hash].js` (Angular lazy) | the lazy feature module | high |
| `chunk-vendors.[hash].js` | dependencies | skip |
| `runtime.[hash].js`/`webpack` | the loader | skip |
| `polyfills.[hash].js` | polyfills | skip |
| `sw.js`/`service-worker.js` | the precache manifest | high |
| `config.js`/`env.js`/`constants.js` | keys, flags, API bases | highest |
| `_buildManifest.js` | every Next route + chunk | high |
| `_ssgManifest.js` | the SSG/dynamic routes | medium |
| `asset-manifest.json` | the full asset inventory | high |
| `precache-manifest.*.js` | the SW asset list | high |
| `*.js.map` | the source map | highest when present |
| `__NEXT_DATA__` | serialized props + `runtimeConfig` | high |

## The in-bundle regions

| Region | Signal |
|---|---|
| head | `webpackChunk`, the string array (obfuscated), the module registry |
| body | endpoints, params, secrets, routes, flags |
| tail | `//# sourceMappingURL=` |
| a module fn | per-file logic (unminified/dev builds) |
| a config block | `process.env`/`DefinePlugin`/env inlines |

## The response-header surface

`SourceMap:`, `X-SourceMap:` — a map reference without a comment;
`content-type` distinguishes a real map from a catch-all.

## The manifest surfaces

`_buildManifest.js`, `asset-manifest.json`, `precache-manifest`,
`sw.js` — the build's own inventory; the complete asset + route list
`main` alone misses.

## The adjacent-surface files

`.git/HEAD`, `.git/config`, `.env`, `backup.*`, `app.zip`, `db.sql`,
`src/`, `static/maps/`, `package.json`, `robots.txt`, `sitemap.xml`,
`README.md`, CHANGELOG.md — a deployment lax enough to ship `.map`
often ships the rest. The map is the lax signal; the adjacent surface
is the bigger leak.

## The per-chunk rule (repeated)

The interesting endpoint is most often in a *page chunk* or a
lazy-loaded module, not `main`. Enumerate every chunk; `main`-only
mining is the common miss.

## The per-role surface

A session-gated or role-gated bundle is a *richer* surface — the
authenticated/admin bundle names routes a guest bundle does not. Fetch
as each available role.
