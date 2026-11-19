# Service-worker and manifest mining — the precache goldmine

## The service-worker surface

`sw.js`/`service-worker.js` precaches the app's real assets — its
`precache-manifest` or `assets` list names every file the app ships,
including lazy chunks the entry page never references directly.

```bash
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.(js|json|map|html)"' | sort -u
curl -s "$BASE/service-worker.js" | grep -oE '(url|revision|precache)[^,}]+' | head -40
```

## The precache manifest

`precache-manifest.<hash>.js` (Workbox) — a `self.__precacheManifest`
array of `{url, revision}` — the complete asset inventory:

```js
self.__precacheManifest = [
  {url:"index.html",revision:"..."},
  {url:"static/js/main.<h>.js",revision:"..."},
  {url:"static/js/5.<h>.chunk.js",revision:"..."}
]
```

Every `url` is an asset — including the lazy/admin chunks `main` never
loads until a route fires.

## The `asset-manifest.json`

CRA/Vue emit `asset-manifest.json` — a `files` map of every built
asset. A complete inventory without crawling:

```bash
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool
```

## The `_buildManifest` (Next) recap

`_buildManifest.js` is the same idea for Next — every route + its
chunk. The manifest is the app's own inventory; it enumerates lazy and
hidden chunks `main` alone would miss.

## The `workbox` runtime config

`workbox` config in `sw.js` — cache names, precache lists, runtime
caching rules — names the assets and sometimes internal routes the SW
caches.

## The mining order on a SW app

```
sw.js -> precache manifest -> every named asset -> each .map sibling
```

The precache list is the authoritative asset set — fetch and mine every
named `.js`, probe every named `.map`.

## The hidden-asset find

The precache list often names an admin/debug/dev asset —
`admin.<hash>.js`, `debug-panel.js`, `internal.<hash>.chunk.js` — that
no route references. A file *named* for the interesting thing is a lead
even before it is fetched.
