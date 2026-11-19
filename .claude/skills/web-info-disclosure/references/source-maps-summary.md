# Source maps — .map files and the front-end's real source — summary

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Signal → route

- .js.map referenced in a bundle comment → bundle_miner --url
- //# sourceMappingURL= present → fetch the map
- sourcesContent in the map JSON → write to --out
- map 404 but inline data-URI map → --file on the bundle

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).
