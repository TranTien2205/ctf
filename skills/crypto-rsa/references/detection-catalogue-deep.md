# Detection catalogue deep — every keygen tell, indexed

## The prime-generation tells

| The tell | The signal | The file |
|---|---|---|
| `q=next_prime(p)` | `fermat` | `fermat*.md` |
| `q=p+k`,`p+2` | `fermat` | `fermat*.md` |
| `random.seed(...)` | `batch-gcd`/regen | `batch-gcd*.md` |
| `getPrime(512)`+`p-1` smooth | `pollard-pm1` | `pollard-pm1*.md` |
| `p`,`q` from a small pool | `batch-gcd` | `batch-gcd*.md` |
| `p=a+x` leak | `coppersmith` | `coppersmith*.md` |

## The exponent tells

| `e=3`/`5`/`17` | `small-e`/`hastad`/`franklin-reiter` |
| `e`~`n` | `wiener`/`boneh-durfee` |
| `d=getPrime(small)` | `wiener`/`boneh-durfee` |
| `e` even / `gcd(e,phi)>1` | `eth-root` |
| `e=1` | `c=m` |

## The relation tells

| `m2=a·m1+b` | `franklin-reiter` |
| `for n in ns: pow(m,e,n)` | `hastad` |
| `pow(m,e1,n);pow(m,e2,n)` | `common-modulus` |
| `sig_correct,sig_faulty` | `crt` Bellcore |
| `m mod pi` × several | `crt` residues |

## The leak tells

| `d`/`phi`/`p`,`q` printed | `factor-from-d`/`rsa-decrypt` |
| `dp`,`dq`,`qInv` | `crt` manual |
| `redact`/`XXXX`/`mask` | `coppersmith`/`crt`/`factor-from-d` |
| `p`/`q`/`d`/`phi`/`dp` in a field | `factor-from-d`/`crt`/`rsa-decrypt` |

## The file

`detection-catalogue.md` is the shorter index; this file the annotated one.
