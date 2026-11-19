# Sibling .map naming conventions — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| app.js → app.js.map 200 | sibling map | bundle_miner --map |
| /static/js/*.js.map in build layout | framework maps | crawl pattern |
| /maps/ or /sourcemaps/ dir | map dir | walk it |

## Falsifier

Falsifier — no sibling maps exist under any convention: the minified bundle alone is the disclosure ceiling.
