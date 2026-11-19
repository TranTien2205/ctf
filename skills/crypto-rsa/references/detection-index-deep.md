# Detection index deep — every read, the file, the attack

## The source reads

| Read | The signal | The file |
|---|---|---|
| `next_prime`/`p+k`/`q=p+2` | `fermat` | `fermat*.md`,`detection-catalogue.md` |
| `getPrime(d)` small | `wiener`/`boneh-durfee` | `wiener*.md`,`boneh-durfee*.md` |
| `random.seed`/`reused p` | `batch-gcd` | `batch-gcd*.md` |
| `p-1` smooth | `pollard-pm1` | `pollard-pm1*.md` |
| `e=3`,no pad | `small-e`/`hastad` | `small-e-root*.md`,`hastad*.md` |
| `m2=a·m1+b` | `franklin-reiter` | `franklin-reiter*.md` |
| `dp`,`dq`,`qInv` | `crt` | `crt*.md` |
| `d`/`phi` | `factor-from-d` | `factor-from-d*.md` |
| `redact`/`XXXX` | `coppersmith`/`crt`/`factor-from-d` | `coppersmith*.md` |

## The numeric reads

| Read | The signal | The file |
|---|---|---|
| `e`=3/5/17 | `small-e`/`hastad`/`franklin-reiter` | `small-e-root*.md`,`hastad*.md` |
| `e`=65537 | default | `detection.md` |
| `e`~`n` | `wiener`/`boneh-durfee` | `wiener*.md`,`boneh-durfee*.md` |
| `gcd(e,phi)>1` | `eth-root` | `eth-root*.md` |
| `n` square | `phi=p(p-1)` | `edge-cases*.md` |
| `n` prime | `phi=n-1` | `edge-cases*.md` |
| `n` count ≥2 | `batch-gcd`/`hastad` | `batch-gcd*.md`,`hastad*.md` |
| `e` count 2 on 1 `n` | `common-modulus` | `common-modulus*.md` |
| `c` count ≥`e` | `hastad` | `hastad*.md` |

## The verify

`pow(m,e,n)==c` / `p*q==n` — the gate on every recovery.
