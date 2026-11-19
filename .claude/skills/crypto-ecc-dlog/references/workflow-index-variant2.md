# Workflow index variant 2 — phases → files → commands, alternate

## Inventory phase

| Step | Files | Command |
|---|---|---|
| parse | `detection*.md` | read |
| dedupe | `per-check*.md` | `Counter(r)` |
| gates | `per-check*.md` | `smoothness`/`Δ`/`#E`/count |

## Solve phase

| Step | Files | Command |
|---|---|---|
| nonce | `per-attack-*.md` | `ecdsa-nonce-reuse`/`hnp-*` |
| dlog | `per-attack-*.md` | `pohlig-hellman`/`bsgs` |
| defect | `per-attack-*.md` | `smart`/`singular`/`ec.py` |

## Close phase

| Step | Files | Command |
|---|---|---|
| verify | `verify*.md` | `E.mul`/`pow` |
| record | `field-notes-*.md` | `post-probe` |
| card | `verified-chains*.md` | `classify_solve` |

## Escalate phase

| Step | Files | Command |
|---|---|---|
| fix | `troubleshoot*.md` | re-read |
| falsify | `falsifiers*.md` | `attempts` |
| next | `decide.py` | rung |
