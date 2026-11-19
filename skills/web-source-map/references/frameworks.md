# Frameworks — per-build-system map and bundle shapes

## webpack / create-react-app

```
/static/js/main.[hash].js
/static/js/[n].[hash].chunk.js
/static/css/main.[hash].css
//# sourceMappingURL=main.[hash].js.map
```

CRA ejects to webpack — the map is `main.[hash].js.map`, and
`sources` carry a `webpack://` scheme. The `main` bundle holds the app
shell; per-route logic is in the numbered `chunk` files — the
interesting endpoint is often in a page chunk, not `main`.

```bash
# every chunk, not just main
curl -s "$BASE/" | grep -oE '/static/js/[^"]+\.js' | sort -u
# each chunk's map
for c in $(curl -s "$BASE/" | grep -oE '/static/js/[^"]+\.js' | sort -u); do
  curl -s -o /dev/null -w "$c.map -> %{http_code}\n" "$BASE$c.map"
done
```

## Next.js

```
/_next/static/chunks/main-[hash].js
/_next/static/chunks/pages/[route]-[hash].js
/_next/static/[buildId]/_buildManifest.js
/_next/static/[buildId]/_ssgManifest.js
```

Next chunks are per-route — the `_buildManifest.js` lists every page
route and its chunk. The interesting endpoint is in the *page* chunk
(`pages/admin-*.js`), not `main`. Fetch the manifest to enumerate every
route the app knows:

```bash
BUILD=$(curl -s "$BASE/" | grep -oE '"buildId":"[^"]+"' | head -1 | cut -d'"' -f4)
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
# -> lists /admin, /api/internal, ... every route
```

`__NEXT_DATA__` in the entry page is a second goldmine — serialized
props, config, sometimes server-injected secrets.

## Vite

```
/assets/index-[hash].js
/assets/[name]-[hash].js
```

Vite ships ES modules — the bundle is often less mangled than webpack's
(output preserves module structure better). Sourcemaps are off in prod
by default (`build.sourcemap` defaults false) — string mining is the
common path. Dev-only paths (`/@fs/`, `/@vite/`, `src/`) leak in dev
builds.

## Vue CLI

```
/js/app.[hash].js
/js/chunk-vendors.[hash].js
/js/[route].[hash].js
```

`app` is the application, `chunk-vendors` the dependencies, per-route
chunks per page. Route definitions (vue-router `path:`/`component:`)
name every page including hidden ones.

## Angular

```
/main.[hash].js
/runtime.[hash].js
/polyfills.[hash].js
```

Angular lazy-loads feature modules into numbered chunks — the admin
module is often a lazy chunk (`[n].[hash].js`) loaded on a route the UI
hides. `main` holds the routes table.

## The generic fingerprint table

| Build | Marker | Map guess |
|---|---|---|
| webpack | `webpackChunk`, `__webpack_require__` | `<bundle>.js.map` |
| CRA | `/static/js/main.[hash].js` | `main.[hash].js.map` |
| Next.js | `/_next/static/`, `__NEXT_DATA__` | per-chunk `*.js.map` |
| Vite | `/assets/index-[hash].js`, `import.meta` | `[asset].js.map` (rare in prod) |
| Vue | `/js/app.[hash].js`, `chunk-vendors` | `app.[hash].js.map` |
| Angular | `runtime.`, `polyfills.`, `main.` | `main.[hash].js.map` |
| esbuild | `(()=>{` IIFE, minimal runtime | `index.js.map` |
| Rollup | `var ` + module fns, `exports.` | `bundle.js.map` |

## The per-route rule

The single most common miss: mining only `main` and missing the
per-route/lazy chunk that holds the interesting endpoint. Enumerate
EVERY script the page loads — and the manifest lists ones it lazy-loads
— before deciding the bundle is thin.
