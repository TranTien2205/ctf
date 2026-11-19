# Detection map — the observation → the file, navigable

## By handout shape

| Handout | First file |
|---|---|
| two sigs same `r` | `per-attack-ecdsa-nonce-reuse.md` → `ecdsa-nonce-reuse-deep.md` |
| many sigs distinct `r`, `k` bounded | `per-attack-hnp-ecdsa.md` → `hnp-ecdsa-deep.md` |
| `(t,u)` pairs | `per-attack-hnp.md` → `hnp-deep.md` |
| `h = g^x mod p` | `per-attack-pohlig-hellman.md` → `pohlig-hellman-deep.md` |
| bounded `x` | `per-attack-bsgs.md` → `bsgs-deep.md` |
| unknown order | `per-attack-smoothness.md` → `smoothness-deep.md` |
| `#E == p` | `per-attack-smart.md` → `smart-attack-deep.md` |
| `Δ == 0` | `per-attack-singular.md` → `singular-ec-deep.md` |
| point oracle | `per-attack-invalid-curve.md` → `invalid-curve-deep.md` |

## By family

| Family | Files |
|---|---|
| nonce | `per-family-nonce.md`,`*nonce*.md`,`hnp*.md` |
| dlog | `per-family-dlog.md`,`pohlig-*.md`,`bsgs-*.md`,`smoothness-*.md` |
| defect | `per-family-curve-defect.md`,`smart-*.md`,`singular-*.md`,`invalid-*.md` |

## By procedure

| Phase | Files |
|---|---|
| read | `detection*.md`,`recon-order.md`,`cipher-identification.md` |
| discriminate | `detection-matrix.md`,`detection-playbook.md`,`per-family-*.md` |
| solve | `payload-dictionary*.md`,`per-attack-*.md`,`probe-order.md` |
| verify | `verify*.md`,`evidence*.md` |
| record | `field-notes-index.md`,`negative-results*.md`,`checklist*.md` |
| escalate | `falsifiers*.md`,`decide.py` |
