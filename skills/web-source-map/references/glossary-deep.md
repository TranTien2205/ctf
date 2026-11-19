# Glossary (deep) — the full vocabulary

## Bundle and build

- **bundle** — the minified JavaScript the app ships; the app's
  client-side logic collapsed into one or more files
- **chunk** — a code-split piece of the bundle (`[n].chunk.js`,
  per-route); the loader splits output into a main bundle plus chunks
- **vendor bundle** (`chunk-vendors`, `vendor.js`) — the third-party
  dependency bundle; skip for app recon
- **runtime/loader** (`runtime.js`, webpack bootstrap) — the code that
  loads the chunks; skip
- **lazy chunk** — a chunk loaded on a route/guard, not on page load;
  often the admin/feature module
- **entry** — the first script the page loads; the app shell
- **build manifest** — `_buildManifest.js`/`asset-manifest.json` —
  the build's own inventory of every route and asset
- **precache manifest** — the service worker's `self.__precacheManifest`
  asset list
- **source map** (`*.js.map`) — a v3 JSON mapping minified positions to
  original source
- **`sources`** — the map's list of original file paths (often a
  `webpack://` scheme)
- **`sourcesContent`** — the map's inlined original source text
- **`sourceMappingURL`** — the `//#` comment naming the map (a URL or
  an inline `data:` URI)
- **`sourceRoot`** — the map's path prefix applied to `sources`
- **`names`** — the map's original identifier list
- **`mappings`** — the VLQ position map (rarely needed for recon)

## Build systems

- **webpack** — `webpackChunk`, `__webpack_require__`, `webpack://` source
  scheme
- **CRA** — create-react-app; `/static/js/main.[hash].js`
- **Next.js** — `/_next/static/`, `__NEXT_DATA__`, `_buildManifest`,
  per-page chunks, `/api/*` routes
- **Vite** — `/assets/index-[hash].js`, `import.meta`, ESM output
- **Vue CLI** — `/js/app.` + `chunk-vendors.`, `VUE_APP_*`
- **Angular** — `main.`/`runtime.`/`polyfills.`, lazy feature chunks
- **esbuild** — `(()=>{` IIFE, minimal runtime
- **Rollup** — module fns + `exports.`

## Signals and leads

- **endpoint string** — a `"/api/..."` literal the client calls
- **route** — a `path:`/`component:`/`Route`/`loadChildren` definition;
  client-side unless it maps to a server path
- **param** — a request key the client sends (an injection point)
- **feature flag** — a `feature.*`/`flags.*`/`config.*`/`debug` gate the
  client checks
- **route guard** — `requiresAuth`/`canActivate`/`PrivateRoute` — a
  client-side check on a route
- **secret candidate** — a high-entropy/structured string that may be a
  credential; a candidate until it verifies live
- **internal host** — `internal.svc`/`api.internal.*`/`postgres://` — a
  target for SSRF reach
- **`__NEXT_DATA__`** — Next serialized props + `runtimeConfig`
- **`process.env`/`DefinePlugin`** — build-inlined env values
- **env prefix** — `REACT_APP_*`/`NEXT_PUBLIC_*`/`VUE_APP_*`/`VITE_*`

## Discipline

- **lead** — a bundle string claiming something exists; surface/claim
  evidence until verified
- **finding** — a lead verified live + exploited by its class
- **catch-all** — an SPA fallback returning `200 text/html` for any path;
  not a map
- **traversal** — a `sources` path escaping `--out`; rejected, counted
- **catalogue** — this class's evidence level: no local verified solve
