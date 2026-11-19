# Webpack internals — reading the webpack bundle specifically

## The webpack runtime

A webpack bundle wraps a module registry in a bootstrap:

```js
/******/ (function(modules) {
/******/   var installedModules = {};
/******/   function __webpack_require__(moduleId) { ... }
/******/   return __webpack_require__(0);
/******/ })({0: function(module,exports,__webpack_require__){...}, ...})
```

Each numbered/-keyed `function(module, exports, __webpack_require__){...}`
is one original file, minified. `__webpack_require__(n)` is the import.

## The chunk map

`webpackChunk` / `self["webpackChunk*"]` — the lazy-load registry. The
bootstrap's `installedChunks` + the `u = function(e){return
"static/js/"+e+"."+{id:hash}[e]+".chunk.js"}` naming fn map chunk ids to
files — read it to enumerate every lazy chunk without the manifest.

```bash
# the chunk-name mapping fn — enumerates lazy chunks
grep -oE '"static/js/"\s*\+\s*\w+\s*\+\s*"\."?[^,}]*' bundle.js | head
grep -oE '\{[0-9,:"a-f]{20,}\}\[\w+\]' bundle.js   # the id->hash table
```

## The module-id → file read

When the map is absent, the bundle's module ids still hint at files —
a `/*!*****************!*\n  !*** ./src/api.js !***` comment marker
survives in non-minified builds, and the `s` (`source`) field in a map
names it. In dev builds the module *name* is the file path.

```bash
# webpack module-path markers in unminified/dev bundles
grep -oE '!\*\*\*\s+[^*]+\s+\*\*\*!' bundle.js | sort -u
grep -oE '\./src/[A-Za-z0-9_./-]+\.js' bundle.js | sort -u
```

## The DefinePlugin / ProvidePlugin inlines

`DefinePlugin` bakes `process.env.*` into the bundle as literals;
`ProvidePlugin` aliases globals. The inlined config block is a
recognizable object:

```bash
grep -oE 'process\.env\s*=\s*\{[^{}]+\}' bundle.js
grep -oE '(NODE_ENV|API_URL|BASE_URL|REACT_APP_[A-Z_]+|PUBLIC_URL)\s*[:=]\s*"[^"]*"' bundle.js
```

## The `webpack://` source scheme

A map's `sources` carry `webpack://<name>/<path>` —
`webpack://app/./src/api.js`. `bundle_miner --source-scheme normalise`
strips `webpack://app/` to `src/api.js`; `reject` refuses it. A
`webpack://` source is the bundler's namespace, not a host.

## The split-chunks vendor boundary

`optimization.splitChunks` separates `node_modules` into a vendor chunk
(`chunk-vendors`, `vendor.[hash].js`) — skip it for recon (it is
react/lodash, not app logic). The app logic is in `main`/`app`/page
chunks and lazy-route chunks.

## The hot-module / dev artifacts

`webpackHotDevClient`, `module.hot`, `webpack-dev-server`, a
`//# sourceURL=` per-module marker — dev-build artifacts. Their presence
means a dev build, which usually means richer strings, sourcemaps on,
and debug endpoints.
