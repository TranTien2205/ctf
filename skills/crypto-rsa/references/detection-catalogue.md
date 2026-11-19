# Detection catalogue — every signal → the attack it implies

## Moduli-count signals

| Signal | Attack |
|---|---|
| `n` count ≥ 2, one gen | `batch-gcd` |
| `n` count ≥ 2, different `c`, same `m` | `hastad` |
| `n` count = 1 | single-modulus — the whole table |

## Exponent signals

| Signal | Attack |
|---|---|
| `e` = 3/5/17/257 | `small-e-root`/`hastad`/`franklin-reiter` |
| `e` = 65537 | default — look elsewhere |
| `e` ~ `n` | `wiener`/`boneh-durfee` |
| `e` coprime to φ fails | `eth-root` |
| 2 `e` on 1 `n`, gcd=1 | `common-modulus` |

## Keygen signals

| Signal | Attack |
|---|---|
| `next_prime`/`p+k`/`q=p+2` | `fermat` |
| `getPrime(small)` for `d` | `wiener`/`boneh-durfee` |
| `random.seed`/`reused p` | `batch-gcd` |
| `p-1` smooth | `pollard-pm1` |
| `e=3`, no pad | `small-e-root`/`hastad` |
| `m2=a·m1+b` | `franklin-reiter` |

## Leak signals

| Signal | Attack |
|---|---|
| `d`/`phi` printed | `factor-from-d`/`rsa-decrypt` |
| `dp`,`dq`,`qInv` | `crt` |
| `p` high/low bytes | `coppersmith-high-bits`/`-core` |
| `m` partial | `coppersmith` partial-message |
| correct+faulty sig | `crt` Bellcore |
| `p`,`q` held | `rsa-decrypt`/`eth-root` |

## Format signals

| Signal | Attack |
|---|---|
| public `.pem` | `n`,`e` only |
| partial private `.pem` | `crt`/`coppersmith`/`factor-from-d` |
| `.json`/`list` of `n` | `batch-gcd` |
| a `.txt` of `n`,`e`,`c` | the sheet → the discriminator |

## The degenerate signals

| Signal | Handling |
|---|---|
| `n` a perfect square | `phi=p(p-1)` |
| `n` prime | `phi=n-1` |
| `n=p·q·r` | `phi=∏(pi-1)` |
| `m=c` (no wrap) | `m` itself |
