# Per-file — the yield per asset file

## The entry/main bundle (`main.js`, `app.js`, `index.js`)

The app shell — the route table, the root config, the entry logic.
Yields: the routes table, the root endpoints, the inlined config.
Mine first, but never only.

## The page/route chunk (`[n].chunk.js`, `pages/x-*.js`, lazy module)

A per-route or lazy-loaded module — the route's specific logic and
endpoints. Yields: the hidden admin/feature endpoints `main` never
shows. The most common high-value find — fetch every chunk.

## The vendor bundle (`chunk-vendors`, `vendor.js`)

The dependencies — `react`, `vue`, `axios`, `lodash`. Skip for recon;
it is library code, not app logic. `--skip-node-modules` drops it.

## The runtime/loader (`runtime.js`, webpack bootstrap)

The chunk-loading machinery — skip; it carries no app logic beyond the
chunk map (which `webpackChunk` exposes for chunk enumeration).

## The config file (`config.js`, `env.js`, `constants.js`)

The standalone config — keys, flags, API bases, hosts. Highest
secret/flag density per byte — always mine.

## The service worker (`sw.js`, `service-worker.js`)

The precache manifest — every asset the app ships, including lazy/admin
chunks. Yields: the complete asset inventory + cached internal routes.

## The build manifest (`_buildManifest.js`, `asset-manifest.json`)

The build's own inventory — every route + its chunk. Yields: the
complete route list including hidden pages.

## The map (`*.js.map`)

The source map — `sourcesContent` recovers the original commented
source. Yields: the real code — sinks, keys, comments, the flag. The
highest single-file yield when present.

## The entry page (`/`)

The script inventory, `__NEXT_DATA__`/`runtimeConfig`, the SPA root.
Yields: the bundle set + serialized config.

## The polyfills (`polyfills.js`)

Browser shims — skip; no app logic.

## The per-file priority

| File | Mine for |
|---|---|
| `config.js`/`env.js` | keys, flags, hosts — first |
| a `.map` | recovered source — first |
| page/lazy chunks | hidden endpoints — first |
| `main`/`app` | routes, config, endpoints |
| `sw.js`/manifest | the asset/route inventory |
| entry page | scripts, `__NEXT_DATA__` |
| `chunk-vendors`/`runtime`/`polyfills` | skip |
