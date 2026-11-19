# Source maps — .map files and the front-end's real source — surface variants

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| .js.map referenced in a bundle comment | map exists | bundle_miner --url |
| //# sourceMappingURL= present | map link | fetch the map |
| sourcesContent in the map JSON | original sources recoverable | write to --out |
| map 404 but inline data-URI map | embedded map | --file on the bundle |

## Variant-specific traps

- --source-scheme normalise vs reject: a 'sources' path escaping --out is rejected and counted — that rejection is a security check.
- A map can be per-chunk: webpack emits many; --max-scripts bounds the crawl.
- Minified source without maps still leaks endpoint strings and secret candidates.
- A 'sourcesContent' that is null means the map has names/mappings but not content — sources must be reconstructed differently.

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).

## Cross-references

`tools-bundle-miner.md` · `../web-source-map/` · `secrets-in-js.md`
