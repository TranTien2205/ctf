# Detection surface — the files and regions that carry signal

## The asset inventory

| File | Carries |
|---|---|
| entry page (`/`) | `<script src>` list, `__NEXT_DATA__`, SPA root |
| `main.[hash].js` | the app shell, route table, config |
| `[n].chunk.js` / page chunks | per-route logic, hidden endpoints |
| `chunk-vendors.[hash].js` | dependencies — skip |
| `runtime.[hash].js` | the webpack loader — skip |
| `app.[hash].js` (Vue) | the app + routes |
| `index-[hash].js` (Vite) | the ESM entry |
| `sw.js` | the precache manifest — every asset |
| `config.js`/`env.js` | keys, flags, API bases |
| `_buildManifest.js` | every Next.js route + its chunk |
| `asset-manifest.json` | the full asset inventory |
| `*.js.map` | the source map → original source |

## The in-bundle regions

| Region | Signal |
|---|---|
| head | `webpackChunk`, the string array (obfuscated) |
| body | endpoints, params, secrets, routes |
| tail | `//# sourceMappingURL=` |
| a module fn | per-file logic when unminified |

## The response-header surface

`SourceMap:`, `X-SourceMap:` — a map reference without a comment.
`bundle_miner` checks these.

## The adjacent-surface

`.git`, `.env`, `backup.*`, `src/`, `static/maps/` — a host lax enough
to ship `.map` often ships the rest. The map is the signal to probe
the broader disclosure surface.

## The per-chunk rule

The interesting endpoint is most often in a *page chunk* or a
lazy-loaded module, not `main`. Enumerate every chunk; `main`-only
mining is the common miss.
