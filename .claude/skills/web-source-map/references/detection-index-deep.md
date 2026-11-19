# Detection index (deep) — the complete signal catalogue

## By artifact layer

| Layer | Signals |
|---|---|
| entry page | `<script src>`, `__NEXT_DATA__`, `buildId`, SPA root `<div id=root/app>`, `<link rel=modulepreload>` |
| bundle head | `webpackChunk`, `__webpack_require__`, `(function(){`, `(()=>{`, `import`/`import.meta` |
| bundle body | endpoint strings, secrets, routes, params, flags, config |
| bundle tail | `//# sourceMappingURL=`, inline `data:` map |
| response headers | `SourceMap:`, `X-SourceMap:`, `content-type` |
| manifest | `_buildManifest.js`, `_ssgManifest.js`, `asset-manifest.json`, `precache-manifest`, `sw.js` |
| map file | `sources`, `sourcesContent`, `names`, `mappings`, `sourceRoot` |
| adjacent | `.git/HEAD`, `.env`, `backup.*`, `src/`, `config.js`, `robots.txt` |

## By goal

| To find | The signal |
|---|---|
| every endpoint | fetch/axios call sites, `"/api/..."` literals, route defs |
| every route | `path:`/`component:`/`Route`/`loadChildren`, `_buildManifest`, lazy `import()` |
| every secret | JWT/`AKIA`/`sk_`/`ghp_`/`AIza` prefixes, `apiKey`/`token`/`secret` assigns, `process.env`, `-----BEGIN` |
| every flag | `feature.`/`flags.`/`config.`/`debug`/`internal`/`isAdmin`/`meta.requiresAuth` |
| every param | `?x=`/`{x:`/`append("x"`/template-literal/`body:`/`data:` keys |
| the real source | `.map` + `sourcesContent` → `--out` |
| the app structure | `sources` file names, `src/` layout |
| the flag itself | `flag{`, `const FLAG`, comment, env value |
| the internal hosts | `internal.svc`, `api.internal`, `postgres://`, `10.`, `192.168`, `localhost` |
| the gated surface | `meta.requiresAuth`, `PrivateRoute`, `canActivate`, `feature.X` |

## By build system

| Build | Marker | Map guess |
|---|---|---|
| webpack | `webpackChunk`, `__webpack_require__` | `<bundle>.js.map` |
| CRA | `/static/js/main.[hash].js` | `main.[hash].js.map` |
| Next.js | `/_next/static/`, `__NEXT_DATA__` | per-chunk `*.js.map` |
| Vite | `/assets/index-[hash].js`, `import.meta` | `[asset].js.map` (rare) |
| Vue | `/js/app.` + `chunk-vendors.` | `app.[hash].js.map` |
| Angular | `runtime.`+`polyfills.`+`main.` | `main.[hash].js.map` |
| esbuild | `(()=>{`, `__defProp` | `index.js.map` |
| Rollup | `var `+`exports.` | `bundle.js.map` |

## By value

| Signal | Value |
|---|---|
| a live credential | highest |
| a hidden endpoint | high |
| a feature flag / gate | high |
| an internal host | high |
| recovered source | high |
| a route path | medium |
| a param name | medium |
| a flag shape | medium |
| a file name | low-medium |
| a `node_modules` source | low |
