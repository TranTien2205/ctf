# Per-check map — the discriminating test → the attack it selects

## The cheap checks (run first)

| Check | The code | Fires → |
|---|---|---|
| `n` count | `len(set(ns))` | ≥2 → `batch-gcd`/`hastad` |
| `e` count on 1 `n` | `len(set(es))` | 2 → `common-modulus` |
| `c` count, same `m` | `len(cs)` | ≥`e` → `hastad` |
| `e` value | `e` | 3/5/17→small-e; ~`n`→small-d; 65537→default |
| `gcd(e,phi)` | `gcd(e,phi)` | >1 → `eth-root` |
| `isqrt(n)**2` | `isqrt(n)**2==n` | `n=p²` |
| `isPrime(n)` | `sympy.isprime` | `n` prime → `phi=n-1` |
| `factorint(n)` | `sympy.factorint` | smooth `n` → direct |
| `m*e` bits vs `n` | `m.bit_length()*e` | `m^e<n` → root |

## The gcd checks

| Check | Fires → |
|---|---|
| `gcd(ni,nj)>1` | `batch-gcd` |
| `gcd(a^{B!}-1,n)>1` | `pollard-pm1` |
| `gcd(s'^e-m,n)>1` | `crt` Bellcore |
| `gcd(pow(a,e*dp-1,n)-1,n)>1` | `crt` dp |

## The lattice checks

| Check | Fires → |
|---|---|
| CF convergent `k/d` of `e/n`, `d<n^0.25` | `wiener` |
| `f(x,y)` small root, `d<n^0.292` | `boneh-durfee` |
| `f(x)=a+x` small root, `x<n^0.25` | `coppersmith` |

## The leak checks

| Check | Fires → |
|---|---|
| `d`/`phi` present | `factor-from-d`/`rsa-decrypt` |
| `dp`,`dq`,`qInv` present | `crt` |
| `p`-high/low present | `coppersmith-*` |
| `p`,`q` held | `rsa-decrypt`/`eth-root` |
| relation `m2=a·m1+b` | `franklin-reiter` |
| residues `mod pi` | `crt` |

## The verify check

`pow(m,e,n)==c` or `p*q==n` — the gate on every recovery.
