# Detection index variant — the reads by phase

## Phase reads — inventory

| Read | Files |
|---|---|
| artifact type | `detection*.md`,`recon-order.md` |
| group naming | `detection*.md`,`cipher-identification.md` |
| sig inventory | `detection*.md`,`per-family-nonce.md` |

## Phase reads — gates

| Read | Files |
|---|---|
| `r` dedupe | `per-check*.md`,`detection*.md` |
| `smoothness` | `smoothness-deep.md`,`per-family-dlog.md` |
| `Δ` | `per-check*.md`,`singular-ec-deep.md` |
| `#E` | `per-check*.md`,`smart-attack-deep.md` |
| `required_signatures` | `hnp-ecdsa-deep.md`,`per-boundary*.md` |
| validation | `invalid-curve-deep.md` |

## Phase reads — solve

| Read | Files |
|---|---|
| the commands | `payload-dictionary*.md`,`per-attack-*.md` |
| the order | `probe-order.md`,`workflow*.md` |
| the flags | `payload-dictionary*.md` |

## Phase reads — close

| Read | Files |
|---|---|
| verify | `verify*.md`,`evidence*.md` |
| record | `field-notes-index.md`,`negative-results*.md` |
| falsifier | `falsifiers*.md`,`per-falsifier.md` |
| escalate | `decide.py`,`falsifiers*.md` |
