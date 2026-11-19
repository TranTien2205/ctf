# Source maps — .map files and the front-end's real source — deep

A deployed .map file reverses the minification: sourcesContent contains the original code, including endpoints, feature flags, and sometimes secrets. tools/web/bundle_miner.py automates recovery.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no sourceMappingURL, no sibling .map, no inline map: the bundle ships without maps. Mine the minified bundle itself for endpoints and secrets (bundle_miner still lists them).

## Highest-cost traps

- --source-scheme normalise vs reject: a 'sources' path escaping --out is rejected and counted — that rejection is a security check.
- A map can be per-chunk: webpack emits many; --max-scripts bounds the crawl.
- Minified source without maps still leaks endpoint strings and secret candidates.

## Commands

```bash
python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/
python3 tools/web/bundle_miner.py --file bundle.js --map bundle.js.map --out mined/
python3 tools/web/bundle_miner.py --selftest
```

## Cross-references

`tools-bundle-miner.md` · `../web-source-map/` · `secrets-in-js.md`
