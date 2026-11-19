# Secrets in client JavaScript — operational checklist

Front-end bundles routinely ship API keys, internal endpoints, and feature flags. bundle_miner extracts them with file:line; grep patterns catch what recovery misses.

## Checklist

- [ ] python3 tools/web/bundle_miner.py --url <page> --out mined/ (or --file).
- [ ] Read mined sources for: endpoints, feature flags, process.env, hardcoded keys.
- [ ] Grep the bundle for key shapes: AKIA[0-9A-Z]{16}, sk_live_, ghp_, xoxb-, eyJhbGci.
- [ ] Test each key's scope — a public-only key is not a finding; an internal one is.

## Abort conditions

- Key-shaped strings can be examples or decoys — verify scope before claiming.
- Firebase/Supabase 'public' keys are meant to be public — the finding is what they reach.
- Source-map recovery gives file:line for each find — cite that in evidence.

## Falsifier

Falsifier — the bundle contains only public keys and self-references: no disclosure finding. Minified code still merits an endpoint scan.

## Cross-references

`source-maps.md` · `tools-bundle-miner.md`
