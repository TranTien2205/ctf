# tools/web/bundle_miner.py — source-map recovery — case catalogue

Finds .map files (comment, sibling guess, inline data-URI), writes sourcesContent to --out, then mines endpoints, routes, feature flags and secret candidates — with file:line.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --url crawls one level of script src | page-driven | entry page |
| 2 | --file / --map repeatable | bundle/map on disk or URL | targeted |
| 3 | --out writes recovered sources | persist sources | searchable tree |
| 4 | --source-scheme reject is the security check | anti-traversal | default for hostile maps |

## Falsifier

Falsifier — no maps exist and the bundle mines to nothing but minified code: disclosure here is limited to endpoint strings.

## Coverage notes

- --max-scripts/--max-bytes bound the crawl — raise if truncated.
- A map's 'sources' paths are attacker data; the reject counter is a security signal.
- sourcesContent can be null — then the map has mappings but not source text.

## Cross-references

`source-maps.md` · `secrets-in-js.md`
