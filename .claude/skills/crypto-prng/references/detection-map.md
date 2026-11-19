# Detection map — observation → file

## The observation layer → files

| Observe | File |
|---|---|
| generator type | `detection*.md`,`cipher-identification.md` |
| outputs | `per-check*.md` |
| shape/truncation | `edge-cases*.md`,`cipher-identification.md` |
| count | `per-boundary*.md`,`detection-checklist*.md` |

## The gate layer → files

| Gate | File |
|---|---|
| gen fingerprint | `detection-deep.md` |
| count floor | `per-check*.md`,`boundary-cases*.md` |
| raw/consecutive | `edge-cases*.md`,`per-check*.md` |
| seed window | `per-family-seed.md` |

## The solve layer → files

| Attack | Files |
|---|---|
| `lcg-*` | `per-attack-lcg-*.md`,`per-family-lcg.md` |
| `lfsr-*`/`berlekamp` | `per-attack-lfsr-*.md`,`per-attack-berlekamp-massey.md`,`per-family-lfsr.md` |
| `mt19937-clone` | `per-attack-mt19937-clone.md`,`per-family-mt-xorshift.md` |
| `xorshift128` | `per-attack-xorshift128.md` |
| seed-search | `per-family-seed.md` |

## The close layer → files

| Step | Files |
|---|---|
| verify | `verify*.md` |
| record | `field-notes-*.md`,`evidence*.md` |
| falsify | `falsifiers*.md`,`negative-results*.md` |
| escalate | `decide.py` |
