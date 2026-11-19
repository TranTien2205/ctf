# Secrets in client JavaScript — deep

Front-end bundles routinely ship API keys, internal endpoints, and feature flags. bundle_miner extracts them with file:line; grep patterns catch what recovery misses.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the bundle contains only public keys and self-references: no disclosure finding. Minified code still merits an endpoint scan.

## Highest-cost traps

- Key-shaped strings can be examples or decoys — verify scope before claiming.
- Firebase/Supabase 'public' keys are meant to be public — the finding is what they reach.
- Source-map recovery gives file:line for each find — cite that in evidence.

## Commands

```bash
python3 tools/web/bundle_miner.py --url 'https://t/' --out mined/
grep -oE 'AKIA[0-9A-Z]{16}|sk_live_[A-Za-z0-9]+|ghp_[A-Za-z0-9]+' bundle.js
```

## Cross-references

`source-maps.md` · `tools-bundle-miner.md`
