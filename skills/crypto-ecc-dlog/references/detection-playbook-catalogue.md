# Detection playbook catalogue — procedures indexed by branch

## The signature branch

| Step | Files |
|---|---|
| dedupe `r` | `per-check*.md` |
| `k` bound read | `hnp-ecdsa-deep.md`,`per-boundary*.md` |
| count check | `per-boundary*.md` |
| route | `per-family-nonce.md`,`per-attack-*.md` |

## The dlog branch

| Step | Files |
|---|---|
| `smoothness` | `smoothness-deep.md` |
| `x` bound read | `bsgs-deep.md` |
| `h ∈ <g>` check | `per-check*.md` |
| route | `per-family-dlog.md`,`per-attack-*.md` |

## The defect branch

| Step | Files |
|---|---|
| `Δ` check | `per-check*.md` |
| `#E` check | `per-check*.md` |
| `#E` smoothness | `smoothness-deep.md` |
| validation probe | `invalid-curve-deep.md` |
| route | `per-family-curve-defect.md`,`per-attack-*.md` |

## The close branch

| Step | Files |
|---|---|
| verify | `verify*.md`,`evidence*.md` |
| record | `field-notes-*.md` |
| falsify | `falsifiers*.md`,`negative-results*.md` |
| escalate | `decide.py` |
