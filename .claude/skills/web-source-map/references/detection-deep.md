# Detection (deep) — the full discovery methodology

## The discovery funnel

```
entry page -> script inventory -> bundle fetch -> bundle fingerprint ->
map probe -> map decode -> source reconstruction -> string/endpoint mining
```

Each stage is independent — a missing `.map` does not stop string
mining; a missing map does not stop endpoint enumeration.

## Stage 1: the entry-page inventory

The entry page is the manifest of what the app ships:

```bash
# every script src, deduped, sorted
curl -s "$BASE/" | grep -oE 'src\s*=\s*"[^"]+\.js[^"]*"' | sed 's/.*="//;s/"$//' | sort -u
# every module preload / dynamic import hint
curl -s "$BASE/" | grep -oE '(href|src)="[^"]+\.(js|mjs)[^"]*"' | sort -u
# Next.js serialized props + buildId
curl -s "$BASE/" | grep -oE '"buildId":"[^"]+"|"page":"[^"]+"'
```

The script list is the bundle set — every chunk, not just `main`. The
most common miss is mining `main` and skipping the route/lazy chunks.

## Stage 2: the build fingerprint

| Marker in the bundle | Build | Consequence |
|---|---|---|
| `webpackChunk`/`__webpack_require__` | webpack | chunk map + `webpack://` sources |
| `/static/js/main.[hash].js` | CRA (webpack) | `main.[hash].js.map`, numbered chunks |
| `/_next/static/` + `__NEXT_DATA__` | Next.js | `_buildManifest.js`, per-page chunks |
| `/assets/index-[hash].js`, `import.meta` | Vite | ESM output, map rare in prod |
| `/js/app.` + `chunk-vendors.` | Vue CLI | app + vendor + route chunks |
| `runtime.`+`polyfills.`+`main.` | Angular | lazy module chunks |
| `(()=>{` IIFE, no runtime | esbuild | single-file, `index.js.map` |
| `var `+module fns, `exports.` | Rollup | `bundle.js.map` |

## Stage 3: the map probe

For each bundle, three map routes — in order:

```bash
# 1. the sourceMappingURL comment in the bundle tail
curl -s "$B" | tail -c 400 | grep -oE 'sourceMappingURL=[^ ]+'
# 2. the sibling guess <bundle>.js.map
curl -s -o m.json -w '%{http_code} %{content_type}\n' "$B.map"
# 3. the response-header map (SourceMap: / X-SourceMap:)
curl -sI "$B" | grep -iE 'sourcemap'
```

A `200 application/json` starting `{"version":3` is a real map. A `200
text/html` is the SPA catch-all, not a map.

## Stage 4: the map decode

A real map is JSON — `sources` + `sourcesContent` + `names` +
`mappings`. `bundle_miner --out` reconstructs the tree; the gold is
`sourcesContent`, the original commented source.

## Stage 5: the mining pass

Map present → read recovered source for sinks/keys/logic. Map absent →
string-mine every bundle for endpoints/params/flags/secrets. Both feed
the same lead list.

## The completeness check

The detection is done only when EVERY loaded chunk is fingerprinted and
probed, and the manifest's lazy-route chunks are included. A partial
inventory yields a partial surface.
