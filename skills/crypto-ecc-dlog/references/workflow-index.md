# Workflow index — the phases → the files

## Phase map

| Phase | Files | Command |
|---|---|---|
| inventory | `detection*.md`,`recon-order.md` | read the handout |
| discriminate | `cipher-identification.md`,`detection-matrix.md` | `smoothness --n`, `r` scan |
| solve | `payload-dictionary*.md`,`per-attack-*.md` | `crypto_attack.py <id>` |
| verify | `verify*.md`,`evidence*.md` | `x·G == Q` / `g^x == h` |
| record | `field-notes-index.md`,`negative-results*.md` | `post-probe`,`classify_solve` |
| escalate | `falsifiers*.md`,`troubleshoot*.md` | `decide.py` |

## Family workflows

| Family | Files |
|---|---|
| nonce | `per-family-nonce.md`,`ecdsa-nonce-reuse-deep.md`,`hnp-ecdsa-deep.md`,`hnp-deep.md` |
| dlog | `per-family-dlog.md`,`pohlig-hellman-deep.md`,`bsgs-deep.md`,`smoothness-deep.md` |
| defect | `per-family-curve-defect.md`,`smart-attack-deep.md`,`singular-ec-deep.md`,`invalid-curve-deep.md` |

## The close

`verify*.md` → `field-notes-index.md` → `closing-index.md`.
