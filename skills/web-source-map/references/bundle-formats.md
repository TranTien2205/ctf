# Bundle formats — reading each bundler's output shape

## webpack (the runtime-wrapped shape)

```js
(self["webpackChunkapp"]=self["webpackChunkapp"]||[]).push([[ids],{
  id1: (module,exports,__webpack_require__)=>{...},
  ...
}]);
```

- a `webpackChunk` push = a chunk; the object is the module registry
- `__webpack_require__` = the import fn
- `webpack://` source scheme in maps
- `DefinePlugin`/`ProvidePlugin` inlines env

## Rollup (the flat-module shape)

```js
var app = (function () {
  'use strict';
  // module fns concatenated
  var exports = {};
  function m1(){...}
  ...
  return { main: m_entry };
})();
```

- flat modules, `exports.`/`module.exports`, no chunk registry
- `bundle.js.map`, a simpler module structure than webpack

## esbuild (the IIFE shape)

```js
(() => {
  var __defProp = ...;
  // esbuild helpers
  // then the app modules
})();
```

- `(()=>{` IIFE, `__defProp`/`__export` helpers, minimal runtime
- `index.js.map`; output is often the most readable

## Vite/Rollup ESM (the module shape)

```js
import {x} from './chunk-hash.js';
// real ESM imports/exports preserved
```

- `import.meta`, `import()`, ESM structure — the most readable
- `import.meta.env.VITE_*` for env

## UMD (the universal shape)

```js
(function(root,factory){typeof exports==='object'?factory(exports):...})(this,function(exports){...});
```

- a UMD wrapper — library output, less common for an app

## The CRA/webpack bundle path

```
/static/js/main.[hash].js        # the app
/static/js/[n].[hash].chunk.js   # per-route/lazy chunks
/static/css/main.[hash].css
```

## The fingerprint table

| Marker | Bundler |
|---|---|
| `webpackChunk`, `__webpack_require__` | webpack |
| `(function(){var modules={...};__webpack_require__` | webpack (older) |
| `var app=(function(){...})();` + `exports.` | Rollup |
| `(()=>{var __defProp=...` | esbuild |
| `import`, `import.meta`, `from './chunk'` | Vite/ESM Rollup |
| `self["webpackChunk*"].push` | webpack (modern) |

## The read per format

| Format | Read |
|---|---|
| webpack | the module registry; `__webpack_require__` boundaries; `webpack://` sources |
| Rollup | the flat module fns; `exports.` shapes |
| esbuild | the IIFE + `__defProp` helpers — often near-readable |
| Vite/ESM | the `import` graph — the most readable; `import()` lazy chunks |
