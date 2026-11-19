# Source maps — .map files and the front-end's real source — operational checklist

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Checklist

- [ ] Identify the bundle(s) from the page's <script src> tags.
- [ ] python3 tools/web/bundle_miner.py --url <page> --out mined/ — crawls script srcs, fetches maps, writes sourcesContent.
- [ ] For a map you already have: --map <path-or-url>. For a bundle on disk: --file <path>.
- [ ] Read recovered sources: endpoints, routes, feature flags, process.env refs, secret candidates with file:line.
- [ ] sources paths are attacker-controlled: --source-scheme reject refuses traversal out of --out.

## Abort conditions

- --source-scheme normalise vs reject: a 'sources' path escaping --out is rejected and counted — that rejection is a security check.
- A map can be per-chunk: webpack emits many; --max-scripts bounds the crawl.
- Minified source without maps still leaks endpoint strings and secret candidates.

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).

## Cross-references

`tools-bundle-miner.md` · `../web-source-map/` · `secrets-in-js.md`
