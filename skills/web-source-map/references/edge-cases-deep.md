# Edge cases (deep) — the unusual bundle and map shapes

## The inline source map

The map is a `data:` URI at the bundle's tail:

```
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjoz...
```

Decode: base64-decode the segment after `base64,` — the result is the
`.map` JSON. `bundle_miner` handles inline maps; by hand, extract and
decode. Some inline maps use `data:application/json` URL-encoded, not
base64 — URL-decode instead.

## The chained / multi-level map

A `.map` whose `sources` point to intermediate build artifacts (TS →
babel → webpack), sometimes with its own `sourceMappingURL` — a build
chain. Follow the innermost map for the true original source, or mine
each level's `sourcesContent` if present.

## The `sourceRoot` resolution

`sourceRoot` prefixes every `sources` entry — `webpack://app/` +
`./src/index.js` resolves to `webpack://app/./src/index.js`. `bundle_miner
--source-scheme normalise` strips the scheme+root to a writable path; a
manual decode must apply `sourceRoot` then normalise.

## The obfuscated bundle

String-array obfuscation (`var _0x1a2b=['...']` + `_0x1a2b[3]` lookups),
control-flow flattening, encoded strings. The literals exist in a packed
array at the head; the endpoints survive as strings even when the logic
is unreadable. `strings` + shape-grep, or extract/decode the array.

## The WASM-backing app

The `.js` is a loader for a `.wasm` — the real logic is compiled. The
bundle still names endpoints in its strings, but the logic lives in the
wasm — `strings`/`wasm-decompile` on the `.wasm` is a different recon.

## The server-worker / precache bundle

`sw.js`/`service-worker.js` precaches the real assets — the entry page's
scripts may be a thin shell. Mine the service worker for the precache
manifest (`precache-manifest.*.js`), which names every asset.

## The per-environment bundle

`main.dev.js` vs `main.prod.js`, `?env=dev`, a `.dev`/staging host — the
dev bundle ships sourcemaps, debug flags, dev endpoints, `console.log`
secrets. A dev build is a higher-yield target than prod.

## The authenticated-only bundle

A session-gated app serves the bundle to logged-in users only —
`bundle_miner -H "Cookie: $C"`. The authenticated bundle is a *richer*
surface: routes and endpoints a guest cannot see.

## The flag-in-source case

`const FLAG`, a `// flag{` comment, an env-inlined flag — the flag
itself in client source. Still a *candidate*: `pre-flag` it, prove it
against a live/artifact response.

## The empty `sourcesContent`

`sources` present, `sourcesContent` null — the deployment stripped the
source to save size. You get the file layout, not the text. The file
names are still leads (probe `/src/config/secrets.js` if the host serves
them) but the recovery is partial.
