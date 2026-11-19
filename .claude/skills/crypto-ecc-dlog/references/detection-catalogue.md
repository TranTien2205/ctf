# Detection catalogue — every signal → every route

## The signature signals

| Signal | Route | Deep file |
|---|---|---|
| `r` repeated | `ecdsa-nonce-reuse` | `ecdsa-nonce-reuse-deep.md` |
| `r` distinct + `k` bounded | `hnp-ecdsa` | `hnp-ecdsa-deep.md` |
| `k` bits leaked per sig | `hnp`/`hnp-ecdsa` | `hnp-deep.md` |
| `sign(m)` deterministic | RFC 6979 — no reuse on same `m` | `edge-cases-deep.md` |
| `k` = timestamp | `hnp-ecdsa --nonce-bound <ts>` | `hnp-ecdsa-deep.md` |

## The dlog signals

| Signal | Route | Deep file |
|---|---|---|
| `ord(g)`/`#E` smooth | `pohlig-hellman` | `pohlig-hellman-deep.md` |
| `x` bounded / `n` small | `bsgs` | `bsgs-deep.md` |
| `p-1 = 2q` | dead end — not this attack | `boundary-cases.md` |
| `ord` unknown | `smoothness --n` | `smoothness-deep.md` |

## The curve signals

| Signal | Route | Deep file |
|---|---|---|
| `#E == p` | `smart_attack` | `smart-attack-deep.md` |
| `Δ == 0` | `singular_ec` | `singular-ec-deep.md` |
| server skips validation | invalid curve | `invalid-curve-deep.md` |
| `#E` prime / near-`p` | generic-hard — protocol bug | `boundary-cases.md` |
| pairing-friendly curve | MOV/Frey-Rück — flag & move on | `per-family-curve-defect.md` |

## The format signals

| Signal | Route | Deep file |
|---|---|---|
| `jwt` ES256 | `ecdsa-nonce-reuse` if `r` repeats | `scenarios.md` |
| DER-encoded sig | normalize to `(r,s)` ints | `edge-cases-deep.md` |
| raw message for `z` | hash first (sha256 → int) | `edge-cases-deep.md` |
| compressed `Q` | decompress before verify | `edge-cases-deep.md` |
