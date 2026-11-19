# Bundle lifecycle — how the bundle got to the browser

## The build pipeline

```
source (.ts/.jsx/.vue)
  -> transpile (babel/esbuild/swc — JSX/TS to JS)
  -> bundle (webpack/rollup/vite/esbuild — modules to chunks)
  -> minify (terser/esbuild — names + whitespace gone)
  -> map (a .map per chunk — sources/mappings/sourcesContent)
  -> split (code-split lazy chunks at route/component boundaries)
  -> hash (content-hash filenames — main.a1b2c3.js)
  -> deploy (static host / CDN — the map often dropped here)
```

## What each stage leaves in the artifact

| Stage | Trace in the artifact |
|---|---|
| transpile | `Object.defineProperty`, helper imports, `jsxDEV` in dev |
| bundle | `webpackChunk`/`__webpack_require__`/`import.meta`/module wrappers |
| minify | `t=`/`e=>`/single-letter names, a one-line body |
| map | `//# sourceMappingURL=`, the `.map` sibling, a `SourceMap` header |
| split | `import("./chunk")`, `pages/`/`views/` chunks, `lazy()` calls |
| hash | `main.a1b2c3.js`/`index-Dx4f.js` filenames |
| deploy | `.map` present (debug) or absent (stripped); CDN-offloaded |

## Why the map is often absent

The `.map` ships by accident, not design — a debug deploy, a mis-set
`productionSourceMap`, a `static/maps/` left behind, an inline `data:`
the deployer forgot. Production strips it; the operator checks anyway.

## Why the lazy chunk is the gold

Code-splitting isolates a route's code into a lazy chunk loaded on a
gated path. The admin feature is `admin.chunk.js`, loaded on `/admin` —
the chunk is public even when the route is gated. The manifest names
it; the chunk carries the gated surface.

## Why the config is inlined

`DefinePlugin`/`import.meta.env`/`process.env` replace env refs with
literals at build time — a `process.env.KEY` becomes `"the_value"` in
the output. The bundle carries the deployed env, not a `.env` read.
