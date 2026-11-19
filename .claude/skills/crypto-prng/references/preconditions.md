# Preconditions — every requirement with the check

## `lcg-recover`

| Condition | Check | If violated |
|---|---|---|
| `m` known | `m` present | `lcg-unknown-modulus` |
| ≥3 outs | `len(outputs) >= 3` | can't solve `a`,`c` |
| consecutive+raw | no gap/transform | misaligned |
| `gcd(x1-x0,m)=1` | invertible diff | gather/factor `m` |

## `lcg-unknown-modulus`

| Condition | Check | If violated |
|---|---|---|
| ≥6 outs | `len >= 6` | `gcd` unpinned |
| consecutive+raw | no gap | `gcd` wrong |
| actually LCG | fingerprint | not-affine |

## `lcg-truncated`

| Condition | Check | If violated |
|---|---|---|
| `m`,`a`,`c` known | all present | can't build lattice |
| high-bit leak | `x>>b` shape | wrong shape |
| `low-bits` correct | `b` count | lattice wrong |
| enough outs | `required` heuristic | no short vector |

## `berlekamp-massey`/`lfsr-*`

| Condition | Check | If violated |
|---|---|---|
| ≥2·w bits | `len(bits) >= 2*w` | recurrence unpinned |
| plain LFSR | linear complexity | combiner/other |
| taps convention | 1-indexed-LSB | wrong taps |

## `mt19937-clone`

| Condition | Check | If violated |
|---|---|---|
| 624 outs | `len == 624` | NO clone |
| consecutive+raw | `getrandbits(32)` | not a word |
| no reseed | stable stream | alignment breaks |

## `xorshift128`

| Condition | Check | If violated |
|---|---|---|
| ≥4 outs | `len >= 4` | underdetermined |
| xorshift128 (not +/64) | fingerprint | wrong variant |

## seed-search

| Condition | Check | If violated |
|---|---|---|
| small seed | `time()`/`pid` | CSPRNG → wrong class |
| bounded window | epoch stated | unbounded → can't enumerate |
