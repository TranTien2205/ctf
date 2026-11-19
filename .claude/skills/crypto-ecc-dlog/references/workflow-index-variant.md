# Workflow index variant — procedures → files → commands, indexed

## Inventory phase

| Files | Command |
|---|---|
| `detection*.md`,`recon-order.md` | read handout; `ec.curve` for params |

## Gate phase

| Files | Command |
|---|---|
| `per-check*.md` | `r` dedupe |
| `smoothness-deep.md` | `smoothness --n ord` |
| `per-check*.md` | `Δ`/`#E`/`pow(h,ord,p)` checks |
| `per-boundary*.md` | `required_signatures` |

## Solve phase

| Files | Command |
|---|---|
| `payload-dictionary*.md`,`per-attack-*.md` | `crypto_attack.py <id> ...` |
| `per-attack-smart.md` | `tools/crypto/smart_attack.py` |
| `per-attack-singular.md` | `tools/crypto/singular_ec.py` |
| `per-attack-invalid-curve.md` | `tools/crypto/ec.py` + bsgs/pohlig + CRT |

## Verify phase

| Files | Command |
|---|---|
| `verify*.md` | `ec.py` / `pow(g,x,p)` |

## Record phase

| Files | Command |
|---|---|
| `field-notes-index.md`,`negative-results*.md` | `post-probe`,`classify_solve`,`attempts` |

## Escalate phase

| Files | Command |
|---|---|
| `falsifiers*.md`,`troubleshoot*.md` | `decide.py` rungs |
