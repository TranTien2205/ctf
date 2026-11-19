# tools/web/bundle_miner.py — source-map recovery — operational checklist

Finds .map files (comment, sibling guess, inline data-URI), writes sourcesContent to --out, then mines endpoints, routes, feature flags and secret candidates — with file:line.

## Checklist

- [ ] python3 tools/web/bundle_miner.py --selftest.
- [ ] python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/.
- [ ] Read mined/ for endpoints, routes, env refs, secret candidates with file:line.
- [ ] For a hostile/CTF map: --source-scheme reject refuses 'sources' paths escaping --out.

## Abort conditions

- --max-scripts/--max-bytes bound the crawl — raise if truncated.
- A map's 'sources' paths are attacker data; the reject counter is a security signal.
- sourcesContent can be null — then the map has mappings but not source text.

## Falsifier

Falsifier — no maps exist and the bundle mines to nothing but minified code: disclosure here is limited to endpoint strings.

## Cross-references

`source-maps.md` · `secrets-in-js.md`
