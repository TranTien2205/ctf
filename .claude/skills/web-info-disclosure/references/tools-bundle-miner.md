# tools/web/bundle_miner.py — source-map recovery

Finds .map files (comment, sibling guess, inline data-URI), writes sourcesContent to --out, then mines endpoints, routes, feature flags and secret candidates — with file:line.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url crawls one level of script src | page-driven | entry page |
| --file / --map repeatable | bundle/map on disk or URL | targeted |
| --out writes recovered sources | persist sources | searchable tree |
| --source-scheme reject is the security check | anti-traversal | default for hostile maps |

## Steps

1. python3 tools/web/bundle_miner.py --selftest.
2. python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/.
3. Read mined/ for endpoints, routes, env refs, secret candidates with file:line.
4. For a hostile/CTF map: --source-scheme reject refuses 'sources' paths escaping --out.

## Falsifier

Falsifier — no maps exist and the bundle mines to nothing but minified code: disclosure here is limited to endpoint strings.

## Traps

- --max-scripts/--max-bytes bound the crawl — raise if truncated.
- A map's 'sources' paths are attacker data; the reject counter is a security signal.
- sourcesContent can be null — then the map has mappings but not source text.

## Commands

```bash
python3 tools/web/bundle_miner.py --selftest
python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/ --source-scheme reject
```

## Cross-references

`source-maps.md` · `secrets-in-js.md`
