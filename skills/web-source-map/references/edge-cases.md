# Edge cases — the shapes that break the usual pass

## The inline source map

The map is not a file — it is a `data:` URI at the bundle's tail:

```
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLC...
```

`bundle_miner` handles inline maps; by hand, base64-decode the segment
after `base64,` and treat it as a `.map` file.

## The multi-level map

A `.map` whose `sources` point to *other* generated files, with a
`sourceRoot` or a second `.map` — a build chain (TS → babel → webpack).
Follow the chain or mine the innermost map for the original source.

## The huge bundle

A 10MB `chunk-vendors.js` — mostly dependencies. Skip the vendor bundle
for recon (it is `react`/`lodash`, not app logic); the app logic is in
`main`/`app`/page chunks. `--skip-node-modules` drops the `node_modules`
sources a map would otherwise recover.

## The obfuscated bundle

String-array obfuscation (`_0x1234` lookups), control-flow flattening,
encoded strings — the literals are still there but indirection hides
them. `strings` + a grep for the *shape* (`/api/`, `http`, `token`)
surfaces what the obfuscator could not hide. Deobfuscation is a last
resort; the endpoints survive as strings.

## The no-map app

Production sourcemaps off — the common case. The map is absent, not a
failure; string mining is the path. A minified bundle with readable
strings still yields every endpoint/param/flag.

## The WASM-backing app

The JS is a thin loader for a `.wasm` — the real logic is compiled.
The bundle's strings still name endpoints, but the logic lives in the
wasm — a different recon (`wasm-decompile`, `strings` on the wasm).

## The service-worker / precache bundle

A `sw.js`/`service-worker.js` precaches the real assets — the entry
page's scripts may not be the app's. Mine the service worker for the
precache manifest, which names every asset the app ships.

## The per-environment bundle

`main.dev.js` vs `main.prod.js`, a `config.js` per environment — the
dev bundle may carry more (sourcemaps, debug flags, dev endpoints). A
`?env=dev` or a `.dev` host guess sometimes surfaces the richer bundle.

## The flag-in-source case

The flag is literally in the bundle — a `const FLAG`, a comment, an env
value. It is still a *candidate*: `pre-flag` it, and prove it against a
live response or supplied artifact. A string in the source is not a
submission until it passes the gate.
