# Source maps — .map files and the front-end's real source — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| .js.map referenced in a bundle comment | map exists | bundle_miner --url |
| //# sourceMappingURL= present | map link | fetch the map |
| sourcesContent in the map JSON | original sources recoverable | write to --out |
| map 404 but inline data-URI map | embedded map | --file on the bundle |

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).
