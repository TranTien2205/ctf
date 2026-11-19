# Workflow catalogue deep — procedure → steps → files → commands

## The read procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| parse | extract outputs | `detection*` | — |
| shape | int/hex/float/bit | `edge-cases*` | `norm()` |
| fingerprint | name/gcd/BM/clone | `detection-deep*` | `grep`, gcd, BM |

## The gate procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| count | the floor | `per-check*` | `len(outputs)` |
| rawness | ints, no transform | `edge-cases*` | `norm()` |
| alignment | consecutive, no reseed | `edge-cases*` | — |
| params | `m`/`a,c`/taps/`low-bits`/window | `condition-map`,`preconditions` | source read |

## The solve procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| pick | the param-known column | `decision-table*` | the tuple |
| command | the real flags | `payload-*` | `crypto_attack.py <id>` |
| seed | enumerate window | `seed-search-deep` | `random.seed(ts)` |

## The verify procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| hold back | reserve one output | `verify*` | — |
| predict | emit next | `per-attack-*` | the command |
| compare | bit-for-bit | `verify*` | `==` |

## The close procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| use | forge/decrypt/win | `multi-step-chains*` | — |
| flag | `flag{`/`CTF{` | `evidence*` | grep |
| record | post-probe/pre-flag | `evidence*` | `tools/hooks.py` |
| card | classify_solve | `verified-chains*` | `classify_solve` |

## The escalate procedure

| Step | Detail | Files | Command |
|---|---|---|---|
| fix | convention/variant/norm/align | `troubleshoot*` | re-read |
| falsify | record the kill | `negative-*`/`falsifiers*` | `attempts` |
| next | decide.py rung | `falsifiers*` | `tools/decide.py` |
