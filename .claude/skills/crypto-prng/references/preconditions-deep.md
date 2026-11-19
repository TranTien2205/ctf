# Preconditions deep — every requirement, the check, the failure

## The universal preconditions

| Condition | Check | Failure |
|---|---|---|
| generator is PRNG not CSPRNG | no `urandom`/`secrets` | out of class |
| outputs consecutive | no gaps | misaligned state |
| outputs raw | ints, not transform | wrong model |
| count ≥ floor | `len` vs floor | can't run |

## `lcg-recover` — `m` known, `a`,`c` unknown

| Condition | Check | Failure |
|---|---|---|
| `m` known | `modulus` present | `lcg-unknown-modulus` |
| ≥3 outs | `len>=3` | can't solve `a`,`c` |
| `gcd(x1-x0,m)=1` | the inverse exists | non-invertible — odd diff / factor `m` |

## `lcg-unknown-modulus` — `m` also unknown

| Condition | Check | Failure |
|---|---|---|
| ≥6 outs | `len>=6` | gcd unpinned |
| affine | `gcd(u_i)` nonzero | `gcd→0/1` — not LCG |

## `lcg-truncated` — `a`,`c`,`m` known + `x>>b`

| Condition | Check | Failure |
|---|---|---|
| `a`,`c`,`m` | all present | can't build lattice |
| `x>>b` leak | the high-bit form | wrong model for `mod`/`&` |
| `--low-bits=b` | `b`=dropped count | wrong bound |

## `berlekamp-massey`/`lfsr-*` — bitstream

| Condition | Check | Failure |
|---|---|---|
| ≥2w bits | `len>=2w` | recurrence unpinned |
| plain LFSR | `L` convergent | `L≈n/2` — combiner |
| `--taps`/`--width` (predict) | required | command errors |

## `mt19937-clone` — MT

| Condition | Check | Failure |
|---|---|---|
| 624 outs | `len==624` | NO clone — the hard gate |
| raw `getrandbits(32)` | the word | float/`randint` → wrong |
| consecutive+no reseed | the window | off-window |

## `xorshift128` — xorshift

| Condition | Check | Failure |
|---|---|---|
| ≥4 outs | `len>=4` | underdetermined |
| `xorshift128` (not +/64*) | the variant | wrong state |

## seed-search — bounded seed

| Condition | Check | Failure |
|---|---|---|
| small seed | `time()`/`pid`/id | unbounded → out |
| bounded window | `[issue-slack, now]` | can't enumerate |
