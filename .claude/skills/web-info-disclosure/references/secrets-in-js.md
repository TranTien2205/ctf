# Secrets in client JavaScript

Front-end bundles routinely ship API keys, internal endpoints, and feature flags. bundle_miner extracts them with file:line; grep patterns catch what recovery misses.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| apiKey/token/secret strings in bundle | possible live key | test or note |
| process.env refs in recovered source | build-time values leaked | read each |
| internal URL / admin route strings | route disclosure | probe them |
| firebaseConfig / supabase keys | backend-as-service creds | test scope |

## Steps

1. python3 tools/web/bundle_miner.py --url <page> --out mined/ (or --file).
2. Read mined sources for: endpoints, feature flags, process.env, hardcoded keys.
3. Grep the bundle for key shapes: AKIA[0-9A-Z]{16}, sk_live_, ghp_, xoxb-, eyJhbGci.
4. Test each key's scope — a public-only key is not a finding; an internal one is.

## Falsifier

Falsifier — the bundle contains only public keys and self-references: no disclosure finding. Minified code still merits an endpoint scan.

## Traps

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
