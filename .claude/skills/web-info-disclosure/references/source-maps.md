# Source maps — .map files and the front-end's real source

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| .js.map referenced in a bundle comment | map exists | bundle_miner --url |
| //# sourceMappingURL= present | map link | fetch the map |
| sourcesContent in the map JSON | original sources recoverable | write to --out |
| map 404 but inline data-URI map | embedded map | --file on the bundle |

## Steps

1. Identify the bundle(s) from the page's <script src> tags.
2. python3 tools/web/bundle_miner.py --url <page> --out mined/ — crawls script srcs, fetches maps, writes sourcesContent.
3. For a map you already have: --map <path-or-url>. For a bundle on disk: --file <path>.
4. Read recovered sources: endpoints, routes, feature flags, process.env refs, secret candidates with file:line.
5. sources paths are attacker-controlled: --source-scheme reject refuses traversal out of --out.

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).

## Traps

- --source-scheme normalise vs reject: a 'sources' path escaping --out is rejected and counted — that rejection is a security check.
- A map can be per-chunk: webpack emits many; --max-scripts bounds the crawl.
- Minified source without maps still leaks endpoint strings and secret candidates.
- A 'sourcesContent' that is null means the map has names/mappings but not content — sources must be reconstructed differently.

## Commands

```bash
python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/
python3 tools/web/bundle_miner.py --file bundle.js --map bundle.js.map --out mined/
python3 tools/web/bundle_miner.py --selftest
```

## Cross-references

`tools-bundle-miner.md` · `../web-source-map/` · `secrets-in-js.md`
