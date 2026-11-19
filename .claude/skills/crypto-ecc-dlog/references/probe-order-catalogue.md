# Probe order catalogue — the cheap-first ordering → the files

## The read order → files

| Step | Files |
|---|---|
| parse | `detection*.md` |
| `r` dedupe | `per-check*.md`,`probe-order*.md` |
| `z` convention | `per-check*.md`,`operator-notes*.md` |
| `smoothness` | `smoothness-deep.md`,`probe-order*.md` |
| `Δ`/`#E` | `per-check*.md`,`probe-order*.md` |
| bound reads | `per-boundary*.md`,`probe-order*.md` |
| count | `per-boundary*.md` |
| validation | `invalid-curve-deep.md`,`recon-order*.md` |

## The attack order → files

| Family | Order | Files |
|---|---|---|
| nonce | reuse → lattice | `per-family-nonce*.md`,`probe-order*.md` |
| dlog | PH vs BSGS | `per-family-dlog*.md`,`probe-order*.md` |
| defect | Δ→#E→smooth→validation | `per-family-curve-defect*.md`,`probe-order*.md` |

## The verify → files

`verify*.md` `per-check*.md` `operator-notes*.md`.

## The ordering rationale → files

| Why | Files |
|---|---|
| budget | `probe-order-deep.md`,`falsifiers*.md` |
| cheapest gate first | `probe-order-deep.md` |
| `decide.py` enforces | `falsifiers*.md` |
