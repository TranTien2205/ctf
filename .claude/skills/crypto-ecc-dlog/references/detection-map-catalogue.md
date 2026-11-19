# Detection map catalogue — the observation → the route → the files

## The nonce rows

| Observation | Route | Files |
|---|---|---|
| `r` dup | `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse.md`,`ecdsa-nonce-reuse-deep.md` |
| `k < B`, sigs ≥ count | `hnp-ecdsa` | `per-attack-hnp-ecdsa.md`,`hnp-ecdsa-deep.md` |
| `(t,u)` leak | `hnp` | `per-attack-hnp.md`,`hnp-deep.md` |
| deterministic `k` | RFC 6979 — no reuse on same `m` | `edge-cases-deep.md` |

## The dlog rows

| Observation | Route | Files |
|---|---|---|
| `ord` smooth | `pohlig-hellman` | `per-attack-pohlig-hellman.md`,`pohlig-hellman-deep.md` |
| `x` bounded | `bsgs` | `per-attack-bsgs.md`,`bsgs-deep.md` |
| `ord` unknown | `smoothness` | `per-attack-smoothness.md`,`smoothness-deep.md` |
| `p-1 = 2q` | dead end | `boundary-cases*.md` |

## The defect rows

| Observation | Route | Files |
|---|---|---|
| `#E == p` | `smart_attack` | `per-attack-smart.md`,`smart-attack-deep.md` |
| `Δ == 0` | `singular_ec` | `per-attack-singular.md`,`singular-ec-deep.md` |
| unvalidated `P` | invalid curve | `per-attack-invalid-curve.md`,`invalid-curve-deep.md` |

## The route rows

| Observation | Route | Files |
|---|---|---|
| unknown order | `smoothness` | `smoothness-deep.md` |
| named curve | nonce family | `per-family-nonce.md` |
| `jwt` ES256 | `ecdsa-nonce-reuse` if `r` dup | `scenarios*.md` |
