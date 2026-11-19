# Scenarios index — the challenge shapes → the files

## The signature scenarios

| Scenario | Files |
|---|---|
| two sigs same `r` | `scenarios*.md`,`ecdsa-nonce-reuse-deep.md` |
| `sign(m)` service | `scenarios*.md`,`recon-order*.md`,`hnp-ecdsa-deep.md` |
| JWT pair | `scenarios*.md`,`lead-grammar*.md` |
| leaked `k` bits | `scenarios*.md`,`hnp-deep.md` |

## The dlog scenarios

| Scenario | Files |
|---|---|
| `h = g^x mod p` | `scenarios*.md`,`pohlig-hellman-deep.md`,`bsgs-deep.md` |
| `x` bounded | `scenarios*.md`,`bsgs-deep.md` |
| `p-1` smooth | `scenarios*.md`,`smoothness-deep.md`,`pohlig-hellman-deep.md` |

## The curve scenarios

| Scenario | Files |
|---|---|
| custom `p a b` | `scenarios*.md`,`per-family-curve-defect.md` |
| `#E == p` | `scenarios*.md`,`smart-attack-deep.md` |
| `Δ == 0` | `scenarios*.md`,`singular-ec-deep.md` |
| point oracle | `scenarios*.md`,`invalid-curve-deep.md` |

## The format scenarios

| Scenario | Files |
|---|---|
| DER sig | `edge-cases-deep.md` |
| compressed `Q` | `edge-cases-deep.md` |
| `z` as message | `edge-cases-deep.md` |
| mixed reuse+bias | `edge-cases-deep.md` |
