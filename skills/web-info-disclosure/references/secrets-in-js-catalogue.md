# Secrets in client JavaScript — case catalogue

Front-end bundles routinely ship API keys, internal endpoints, and feature flags. bundle_miner extracts them with file:line; grep patterns catch what recovery misses.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | apiKey/token/secret strings in bundle | possible live key | test or note |
| 2 | process.env refs in recovered source | build-time values leaked | read each |
| 3 | internal URL / admin route strings | route disclosure | probe them |
| 4 | firebaseConfig / supabase keys | backend-as-service creds | test scope |

## Falsifier

Falsifier — the bundle contains only public keys and self-references: no disclosure finding. Minified code still merits an endpoint scan.

## Coverage notes

- Key-shaped strings can be examples or decoys — verify scope before claiming.
- Firebase/Supabase 'public' keys are meant to be public — the finding is what they reach.
- Source-map recovery gives file:line for each find — cite that in evidence.

## Cross-references

`source-maps.md` · `tools-bundle-miner.md`
