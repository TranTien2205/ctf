# Detection checklist (deep) — the exhaustive discovery list

## Is this the right route?

- [ ] a SPA / JS-bundle app (React, Vue, Next, Angular, webpack, Vite)
- [ ] the front-end is the only source (no white-box handout)
- [ ] the rendered page hides routes/endpoints the bundle might name
- [ ] a `//# sourceMappingURL=` or `.map` reference may exist

## Entry-page inventory

- [ ] every `<script src>` listed + deduped
- [ ] every `<link rel=modulepreload>`/`import()`/`preload` captured
- [ ] `__NEXT_DATA__`/`buildId`/`runtimeConfig` parsed (Next)
- [ ] the SPA root marker noted (`<div id="root">`/`<div id="app">`)

## Manifest inventory

- [ ] `_buildManifest.js` (Next) → the route+chunk list
- [ ] `_ssgManifest.js` (Next) → the SSG/dynamic routes
- [ ] `asset-manifest.json` (CRA/Vue) → the full asset map
- [ ] `precache-manifest.*.js`/`sw.js` → the service-worker asset list
- [ ] `manifest.json`/`static/manifest.json` → a possible asset list

## Bundle inventory

- [ ] every chunk named by the page + manifest (not just `main`)
- [ ] the vendor/runtime chunk identified (skip for recon)
- [ ] every lazy `import()`/`loadChildren` chunk enumerated
- [ ] the build fingerprinted (webpack/CRA/Next/Vite/Vue/Angular/esbuild)

## Map inventory

- [ ] `sourceMappingURL` read on every bundle tail
- [ ] `<bundle>.js.map` + `<bundle>.map` + `/static/maps/` probed
- [ ] `SourceMap`/`X-SourceMap` header checked
- [ ] an inline `data:` map identified + decoded
- [ ] real map = `application/json` + `{"version":3`; `text/html` =
      catch-all

## The decision

| Signal | Route |
|---|---|
| a map with `sourcesContent` | read recovered source |
| a map without content | structure leads only |
| no map + strings | string mine every bundle |
| no map + opaque strings | the route may be dead |

## The completeness check

Detection is done only when every loaded chunk is fingerprinted and
every map route is probed. A partial inventory yields a partial surface
— the common miss is `main`-only.
