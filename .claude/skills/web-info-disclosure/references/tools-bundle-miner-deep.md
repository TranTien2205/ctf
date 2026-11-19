# tools/web/bundle_miner.py — source-map recovery — deep

Finds .map files (comment, sibling guess, inline data-URI), writes sourcesContent to --out, then mines endpoints, routes, feature flags and secret candidates — with file:line.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no maps exist and the bundle mines to nothing but minified code: disclosure here is limited to endpoint strings.

## Highest-cost traps

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
