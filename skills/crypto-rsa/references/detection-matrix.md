# Detection matrix — observable × attack

## The counts

| n | e | c | The attack |
|---|---|---|---|
| ≥2 | 1 small, same `m` | ≥`e` | `hastad` |
| ≥2 | 1 small, `m2=a·m1+b` | 2 | `franklin-reiter` |
| ≥2 | any | any | `batch-gcd` |
| 1 | 2, same `m` | 2 | `common-modulus` |
| 1 | 1 | 1 | single-modulus |

## `e` signal

| `e` | The attack |
|---|---|
| 3/5/17 | `small-e`/`hastad`/`franklin-reiter` |
| 65537 | a leak/the primes/a relation |
| `e`≈`n` | `wiener`/`boneh-durfee` |
| `gcd(e,phi)>1` | `eth-root` |
| 1 | `c=m` |

## `n` shape

| `n` | The attack |
|---|---|
| `|p-q|` small | `fermat` |
| `p-1` smooth | `pollard-pm1` |
| `p` bits | `coppersmith` |
| `p²`/prime/multi | degenerate |

## The leak

| `p`/`m` bits | `coppersmith` |
| `d`/`phi`/`p`,`q` | `factor-from-d`/`rsa-decrypt` |
| `dp`,`dq`,`qInv` | `crt` |
| `sig`+fault | `crt` Bellcore |
| `m` residues | `crt` |

## The verify

`pow(m,e,n)==c` / `p*q==n`.
