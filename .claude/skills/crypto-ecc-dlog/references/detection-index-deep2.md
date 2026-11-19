# Detection index deep 2 — the reads indexed by decision, annotated

## Decision 1 — family

| Decide | Files |
|---|---|
| nonce (sigs) | `detection*.md`,`per-family-nonce.md` |
| dlog (`h = g^x`) | `detection*.md`,`per-family-dlog.md` |
| defect (params) | `detection*.md`,`per-family-curve-defect.md` |

## Decision 2 — attack within family

| Decide | Files |
|---|---|
| nonce: reuse/bias/leak | `detection*.md`,`per-attack-*.md` |
| dlog: PH/BSGS | `detection*.md`,`per-attack-*.md` |
| defect: smart/singular/invalid | `detection*.md`,`per-attack-*.md` |

## Decision 3 — flags

| Decide | Files |
|---|---|
| `--order` = `n`/`ord`/`B` | `boundary-cases*.md`,`per-check*.md` |
| `--nonce-*` bound | `per-boundary*.md`,`hnp-*.md` |
| `--sigs` file | `operator-notes*.md` |
| `--t`/`--u`/`--bound` | `hnp-deep.md` |

## Decision 4 — verify/record/escalate

| Decide | Files |
|---|---|
| verify shape | `verify*.md` |
| record shape | `field-notes-*.md`,`evidence*.md` |
| falsifier | `falsifiers*.md`,`per-falsifier.md` |
| rung | `decide.py` |
