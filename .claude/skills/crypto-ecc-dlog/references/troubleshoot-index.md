# Troubleshoot index — the failures → the files

## The nonce failures → files

| Failure | Files |
|---|---|
| `d·G ≠ Q` (reuse) | `troubleshoot*.md`,`ecdsa-nonce-reuse-deep.md` |
| junk lattice | `troubleshoot*.md`,`hnp-*.md` |
| `t`/`u` mismatch | `troubleshoot*.md`,`hnp-deep.md` |
| `k` outlier | `troubleshoot*.md`,`per-check*.md` |

## The dlog failures → files

| Failure | Files |
|---|---|
| PH stall | `troubleshoot*.md`,`pohlig-hellman-deep.md` |
| `g^x ≠ h` | `troubleshoot*.md`,`verify*.md` |
| BSGS no match | `troubleshoot*.md`,`bsgs-deep.md` |
| OOM | `troubleshoot*.md`,`boundary-cases*.md` |

## The defect failures → files

| Failure | Files |
|---|---|
| `#E ≠ p` | `troubleshoot*.md`,`smart-attack-deep.md` |
| `Δ ≠ 0` | `troubleshoot*.md`,`singular-ec-deep.md` |
| `P` rejected | `troubleshoot*.md`,`invalid-curve-deep.md` |
| CRT wrong | `troubleshoot*.md`,`invalid-curve-deep.md` |

## The meta failures → files

| Failure | Files |
|---|---|
| wrong `--order` | `common-mistakes*.md`,`troubleshoot*.md` |
| `--sigs` parse | `operator-notes*.md`,`troubleshoot*.md` |
| `z` convention | `per-check*.md`,`troubleshoot*.md` |
