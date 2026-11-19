# Detection matrix — the signal grid

## `e` signature × leak

| | `e` small | `e`=65537 | `e`~`n` | `gcd(e,phi)>1` |
|---|---|---|---|---|
| no leak | small-e/hastad | look elsewhere | wiener/boneh | eth-root (if p,q) |
| `p`-bits | coppersmith | coppersmith | coppersmith | eth-root |
| `d`/`phi`/`dp` | factor-from-d/crt | factor-from-d/crt | factor-from-d/crt | factor-from-d/crt |
| `p`,`q` | rsa-decrypt/eth-root | rsa-decrypt | rsa-decrypt | eth-root |
| `m2=a·m1+b` | franklin-reiter | franklin-reiter | franklin-reiter | eth-root |

## `n` count × same-`m`

| | `n`≥2, shared prime | `n`≥2, same `m` | `n`=1 |
|---|---|---|---|
| — | batch-gcd | hastad | single-modulus |

## keygen tell × attack

| Tell | Attack |
|---|---|
| `next_prime`/`p+k` | fermat |
| `getPrime(d)` small | wiener/boneh-durfee |
| `random.seed` | batch-gcd |
| `p-1` smooth | pollard-pm1 |
| `e=3`,no pad | small-e/hastad |
| `m2=a·m1+b` | franklin-reiter |
| `dp`,`dq`,`qInv` | crt |
| `d`/`phi` | factor-from-d |
| `redact`/`XXXX` | coppersmith/crt/factor-from-d |
| `n` square/prime/multi | degenerate phi |
