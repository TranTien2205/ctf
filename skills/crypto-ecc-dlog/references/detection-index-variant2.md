# Detection index variant 2 — the reads, indexed by decision

## The `r` decision

| `r` state | Attack | Files |
|---|---|---|
| some equal | `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse.md` |
| all distinct | `hnp-ecdsa`/`hnp` | `per-attack-hnp-*.md` |
| count < 2 | dead | `boundary-cases*.md` |

## The `ord` decision

| `ord` state | Attack | Files |
|---|---|---|
| smooth | `pohlig-hellman` | `per-attack-pohlig-hellman.md` |
| small/bounded | `bsgs` | `per-attack-bsgs.md` |
| `2q` | dead | `boundary-cases*.md` |
| unknown | `smoothness` | `per-attack-smoothness.md` |

## The `Δ`/`#E` decision

| State | Attack | Files |
|---|---|---|
| `Δ == 0` | `singular_ec` | `per-attack-singular.md` |
| `#E == p` | `smart_attack` | `per-attack-smart.md` |
| `#E` smooth | `pohlig-hellman` | `per-family-curve-defect.md` |
| `#E` prime | generic-hard | `boundary-cases*.md` |

## The `k` decision

| `k` state | Attack | Files |
|---|---|---|
| identical | `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse.md` |
| `k < B` | `hnp-ecdsa` | `per-attack-hnp-ecdsa.md` |
| partial | `hnp` | `per-attack-hnp.md` |
| random | dead | `boundary-cases*.md` |

## The validation decision

| State | Attack | Files |
|---|---|---|
| no validation | invalid curve | `per-attack-invalid-curve.md` |
| validates | dead | `boundary-cases*.md` |
