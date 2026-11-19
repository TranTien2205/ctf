# Per-condition deep — every requirement, the failure mode, the file

## `lcg-recover` conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| `m` known | `m`? → wrong attack | `per-attack-lcg-recover.md` |
| ≥3 outs | can't solve | `boundary-cases*` |
| raw+consecutive | wrong `a`,`c` | `edge-cases*` |
| `gcd(x1-x0,m)=1` | `a` non-invertible | `lcg-recover-deep.md` |

## `lcg-unknown-modulus` conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| ≥6 outs | gcd unpinned | `boundary-cases*` |
| consecutive+raw | gcd wrong | `edge-cases*` |
| affine structure | `gcd→0/1` | `lcg-unknown-modulus-deep.md` |

## `lcg-truncated` conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| `a`,`c`,`m` all | can't build lattice | `per-attack-lcg-truncated.md` |
| `x>>b` leak | wrong model | `edge-cases*` |
| `--low-bits=b` dropped | wrong bound | `common-mistakes*` |
| enough `h_i` | under-determined | `boundary-cases*` |

## LFSR conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| ≥2w bits | recurrence unpinned | `boundary-cases*` |
| plain LFSR | `L≈n/2` → combiner | `per-family-lfsr-deep.md` |
| taps convention | wrong poly | `lfsr-*.md` |
| `--taps`+`--width` (predict) | the command errors | `payload-*` |

## `mt19937-clone` conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| 624 outs | NO clone | `boundary-cases*` |
| raw words | garbage clone | `edge-cases*` |
| consecutive+no reseed | off-window | `edge-cases*` |

## `xorshift128` conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| ≥4 outs | underdetermined | `boundary-cases*` |
| `xorshift128` (not +/64*) | wrong state | `xorshift-*.md` |
| consecutive | wrong solve | `edge-cases*` |

## seed-search conditions → failure → file

| Condition | Failure | File |
|---|---|---|
| small seed | not enumerable → out | `per-family-seed*` |
| bounded window | unbounded → out | `boundary-cases*` |
| reproduce the call | seed won't match | `seed-search-deep.md` |
