# Sibling .map naming conventions

The .map file exists but isn't linked — found by convention: same-name.map, .min.js.map, bundle.js.map, or a maps/ directory.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| app.js → app.js.map 200 | sibling map | bundle_miner --map |
| /static/js/*.js.map in build layout | framework maps | crawl pattern |
| /maps/ or /sourcemaps/ dir | map dir | walk it |

## Steps

1. For each discovered .js: fetch <name>.map next to it.
2. Check framework conventions: /static/js/*.map, /dist/*.map, /build/*.map.
3. A directory listing that shows .map files names them all.
4. Feed each found map to bundle_miner --map.

## Falsifier

Falsifier — no sibling maps exist under any convention: the minified bundle alone is the disclosure ceiling.

## Traps

- Webpack/Vite/Next name maps differently — check the bundle's own path shape.
- A .map that 403s may still be fetchable under a different path form.
- Inline data-URI maps don't need a sibling file.

## Commands

```bash
curl -s -o /tmp/r -w '%{http_code}\n' '$BASE/app.js.map'
```

## Cross-references

`source-maps.md` · `tools-bundle-miner.md`
