# tools/web/bundle_miner.py — source-map recovery — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url crawls one level of script src | page-driven | entry page |
| --file / --map repeatable | bundle/map on disk or URL | targeted |
| --out writes recovered sources | persist sources | searchable tree |
| --source-scheme reject is the security check | anti-traversal | default for hostile maps |

## Falsifier

Falsifier — no maps exist and the bundle mines to nothing but minified code: disclosure here is limited to endpoint strings.
