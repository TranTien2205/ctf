# Workflow index catalogue — the procedures → the files → the commands

## Inventory procedures

| Procedure | Files | Command |
|---|---|---|
| artifact parse | `detection*.md`,`recon-order*.md` | read |
| group naming | `detection*.md` | `ec.curve` |

## Gate procedures

| Procedure | Files | Command |
|---|---|---|
| `r` dedupe | `per-check*.md` | `Counter(r)` |
| smoothness | `smoothness-deep.md` | `smoothness --n ord` |
| `Δ`/`#E` | `per-check*.md` | `4a³+27b² mod p`, `E.order()` |
| `h ∈ <g>` | `per-check*.md` | `pow(h, ord, p)` |
| count | `per-boundary*.md` | `required_signatures` |

## Solve procedures

| Procedure | Files | Command |
|---|---|---|
| nonce | `per-attack-ecdsa-nonce-reuse.md`,`hnp-*.md` | `ecdsa-nonce-reuse`/`hnp-ecdsa`/`hnp` |
| dlog | `per-attack-pohlig-hellman.md`,`bsgs` | `pohlig-hellman`/`bsgs` |
| defect | `per-attack-smart.md`,`singular`,`invalid` | `smart_attack`/`singular_ec`/`ec.py` |

## Verify procedures

| Procedure | Files | Command |
|---|---|---|
| curve verify | `verify*.md` | `E.mul(G, d) == Q` |
| field verify | `verify*.md` | `pow(g, x, p) == h` |
| flag | `evidence*.md` | decrypt/forge → `flag{` |

## Record procedures

| Procedure | Files | Command |
|---|---|---|
| ledger | `field-notes-index.md` | `post-probe` |
| card | `verified-chains*.md` | `classify_solve` |
| no's | `negative-results*.md` | `attempts` |

## Escalate procedures

| Procedure | Files | Command |
|---|---|---|
| falsify | `falsifiers*.md` | record |
| fix | `troubleshoot*.md` | re-read |
| next | `decide.py` | rung |
