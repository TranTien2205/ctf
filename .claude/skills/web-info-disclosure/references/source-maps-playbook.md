# Source maps — .map files and the front-end's real source — playbook

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Ordered playbook

1. Identify the bundle(s) from the page's <script src> tags.
2. python3 tools/web/bundle_miner.py --url <page> --out mined/ — crawls script srcs, fetches maps, writes sourcesContent.
3. For a map you already have: --map <path-or-url>. For a bundle on disk: --file <path>.
4. Read recovered sources: endpoints, routes, feature flags, process.env refs, secret candidates with file:line.
5. sources paths are attacker-controlled: --source-scheme reject refuses traversal out of --out.

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).

## Commands

```bash
python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/
python3 tools/web/bundle_miner.py --file bundle.js --map bundle.js.map --out mined/
python3 tools/web/bundle_miner.py --selftest
```
