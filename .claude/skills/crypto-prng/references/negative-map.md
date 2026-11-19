# Negative map — falsifier → the dead claim → the reopen condition

## `lcg-recover` negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| `gcd(x1-x0,m)!=1` all triples | `a` not invertible | `m` factorable / odd diff found |
| `predict!=held` | wrong `m`/non-raw | `m` re-derived / raw inputs |

## `lcg-unknown-modulus` negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| `gcd→0/1` | not affine | it's an LCG on a different leak |
| `gcd`=stubborn multiple | `m` not pinned | more outputs / factor the gcd |
| `lcg-recover` fails | wrong `m` | the gcd's factors are `m` |

## `lcg-truncated` negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| no short vector | `low-bits`/params wrong | recount `b` / fix `a`,`c`,`m` |
| `predict!=held` | wrong model | the leak is `x>>b` not `x mod n` |

## LFSR negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| `L≈n/2` | not plain LFSR | it's a combiner → correlation |
| `predict` diverges all conventions | wrong model | it's Fibonacci/Galois variant |
| `predict` diverges | taps/width/order | re-index / flip bit order |

## `mt19937-clone` negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| <624 | can't clone | a 624 contiguous window appears |
| `predict!=held` | non-raw/gap/reseed | private oracle / one window |
| `predict!=held` | `mt_rand` variant | the PHP MT path exists |

## `xorshift128` negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| `predict!=held` | `128+`/64*/rotating | the `+` variant tool exists |
| `predict!=held` | `Math.random` double | the `128+`+double path |

## seed-search negatives

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| no seed matches | window/wrong-call | widen bound / reproduce the call |
| unbounded window | not enumerable | a smaller seed source named |

## The class negative

| Falsifier | Proves dead | Reopen if |
|---|---|---|
| `predict!=held` everywhere | CSPRNG/keyed | a non-CSPRNG generator named |
