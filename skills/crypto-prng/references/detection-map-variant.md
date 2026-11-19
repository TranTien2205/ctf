# Detection map variant — observation → file, compact

## The observation → the file

| Observation | Files |
|---|---|
| generator type | `detection*`,`cipher-id*` |
| output count | `per-check*`,`boundary*` |
| output shape | `edge-*`,`evasion*` |
| consecutive/raw | `edge-*`,`operator-notes*` |
| `m`/`a`,`c`/taps/`low-bits`/window | `condition*`,`preconditions*` |
| the family | `per-family-*` |
| the attack | `per-attack-*`,`attack-catalogue` |
| the command | `payload-*`,`field-manual*` |
| verify | `verify*` |
| falsifier | `falsifiers*`,`negative-*` |

## The route → the files

| Route | Files |
|---|---|
| `lcg-*` | `lcg-*`,`per-attack-lcg-*`,`per-family-lcg*` |
| `lfsr-*`/`berlekamp` | `lfsr-*`,`per-attack-lfsr-*`,`per-attack-berlekamp*`,`per-family-lfsr*` |
| `mt19937-clone` | `mt-*`,`per-attack-mt19937-clone*`,`per-family-mt-xorshift*` |
| `xorshift128` | `xorshift-*`,`per-attack-xorshift128*` |
| seed-search | `seed-*`,`per-family-seed*` |

## The close → the files

| Step | Files |
|---|---|
| verify | `verify*` |
| record | `evidence*`,`field-manual*` |
| falsify | `falsifiers*`,`negative-*` |
| escalate | `decide.py` |
