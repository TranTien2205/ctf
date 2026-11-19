# Sibling .map naming conventions — case catalogue

The .map file exists but isn't linked — found by convention: same-name.map, .min.js.map, bundle.js.map, or a maps/ directory.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | app.js → app.js.map 200 | sibling map | bundle_miner --map |
| 2 | /static/js/*.js.map in build layout | framework maps | crawl pattern |
| 3 | /maps/ or /sourcemaps/ dir | map dir | walk it |

## Falsifier

Falsifier — no sibling maps exist under any convention: the minified bundle alone is the disclosure ceiling.
