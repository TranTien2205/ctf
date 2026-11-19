# Symmetric-oracle workflow — the ordered path — map

| Observation | Oracle | Next file |
|---|---|---|
| Identical blocks for identical input | ECB encrypt | `ecb-detection.md` |
| Pad-corrupt vs MAC-corrupt differ | CBC padding oracle | `cbc-padding-oracle.md` |
| Two ciphertexts, same nonce | stream/CTR reuse | `ctr-nonce-reuse.md` |
| `hash(secret||m)` construction | prefix MAC | `length-extension.md` |
| Tag checked before decrypt | authenticated | `authenticated-boundary.md` |

Expanded rows and abort conditions: `workflow.md` and `workflow-deep.md`.
