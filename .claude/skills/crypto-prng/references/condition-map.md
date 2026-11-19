# Condition map — attack → conditions → the one-line check

## `lcg-recover` → conditions

| Condition | One-line check |
|---|---|
| `m` known | `modulus` present |
| ≥3 outs | `len(outputs)>=3` |
| consecutive+raw | `outputs` are ints, no gap |
| `gcd(x1-x0,m)=1` | `gcd(outputs[1]-outputs[0],m)==1` |

## `lcg-unknown-modulus` → conditions

| Condition | One-line check |
|---|---|
| ≥6 outs | `len>=6` |
| consecutive+raw | ints, no gap |
| affine | `gcd(u_i)` nonzero |

## `lcg-truncated` → conditions

| Condition | One-line check |
|---|---|
| `a`,`c`,`m` | all three present |
| `x>>b` leak | the output is high bits |
| `--low-bits=b` | `b` = dropped count |
| enough `h_i` | `required` heuristic |

## `berlekamp-massey` → conditions

| Condition | One-line check |
|---|---|
| ≥2w bits | `len(bits)>=2*w` |
| one input form | exactly one of bits/hex/file |
| plain LFSR | `L` convergent `«n/2` |

## `lfsr-recover` → conditions

| Condition | One-line check |
|---|---|
| `--width` | required |
| ≥2w bits | `len>=2*w` |
| taps optional | omit → BM-derived |

## `lfsr-predict` → conditions

| Condition | One-line check |
|---|---|
| `--taps`+`--width` | both required |
| `--count` | the bits to emit |
| register = last w bits | consecutive stream |

## `mt19937-clone` → conditions

| Condition | One-line check |
|---|---|
| 624 outs | `len==624` |
| consecutive+raw | `getrandbits(32)`, no gap |
| no reseed | same generator window |

## `xorshift128` → conditions

| Condition | One-line check |
|---|---|
| ≥4 outs | `len>=4` |
| `xorshift128` (not +/64*) | the variant |
| consecutive | aligned |

## seed-search → conditions

| Condition | One-line check |
|---|---|
| small seed | `time()`/`pid`/id |
| bounded window | `[issue-slack, now]` |
