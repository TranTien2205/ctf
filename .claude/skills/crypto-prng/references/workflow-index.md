# Workflow index — phases → files → commands

## Inventory phase

| Step | Files | Command |
|---|---|---|
| parse | `detection*.md` | read |
| fingerprint | `detection-deep.md` | gcd/BM/clone-test |
| normalize | `edge-cases*.md`,`operator-notes*.md` | decode |

## Gate phase

| Step | Files | Command |
|---|---|---|
| count | `per-check*.md`,`per-boundary*.md` | `len(outputs)` |
| rawness | `edge-cases*.md` | normalize |
| seed window | `per-family-seed.md` | bound epoch |

## Solve phase

| Step | Files | Command |
|---|---|---|
| pick | `cipher-identification.md`,`detection-matrix.md` | the tuple |
| run | `payload-dictionary*.md`,`per-attack-*.md` | `crypto_attack.py <id>` |
| seed | `per-family-seed.md` | `random.seed(ts)` loop |

## Close phase

| Step | Files | Command |
|---|---|---|
| verify | `verify*.md` | `predict == held` |
| record | `field-notes-*.md`,`evidence*.md` | `post-probe` |
| card | `verified-chains*.md` | `classify_solve` |

## Escalate phase

| Step | Files | Command |
|---|---|---|
| fix | `troubleshoot*.md` | re-read |
| falsify | `falsifiers*.md` | `attempts` |
| next | `decide.py` | rung |
