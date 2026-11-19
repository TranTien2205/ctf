# Sibling .map naming conventions — checklist

The .map file exists but isn't linked — found by convention: same-name.map, .min.js.map, bundle.js.map, or a maps/ directory.

## Checklist

- [ ] For each discovered .js: fetch <name>.map next to it.
- [ ] Check framework conventions: /static/js/*.map, /dist/*.map, /build/*.map.
- [ ] A directory listing that shows .map files names them all.
- [ ] Feed each found map to bundle_miner --map.

## Abort conditions

- Webpack/Vite/Next name maps differently — check the bundle's own path shape.
- A .map that 403s may still be fetchable under a different path form.
- Inline data-URI maps don't need a sibling file.

## Falsifier

Falsifier — no sibling maps exist under any convention: the minified bundle alone is the disclosure ceiling.
