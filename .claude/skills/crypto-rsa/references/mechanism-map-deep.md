# Mechanism map deep — primitive → bug → the file

## Wrap → the no-modulo bugs

| The bug | The mechanism | The file |
|---|---|---|
| `small-e-root` | `m^e<n` → `c` a plain power | `small-e-root*.md` |
| `nth-root` | `x=m^n` exact | `nth-root*.md` |
| `hastad` | `m^e<∏ni` → CRT a plain power | `hastad*.md` |

## Gap → the close-prime bug

| `fermat` | `n=a²-b²`, `a` near `√n` | `fermat*.md` |

## Divisor → the shared/smooth bugs

| `batch-gcd` | `gcd(ni,nj)=p` | `batch-gcd*.md` |
| `pollard-pm1` | `gcd(a^{B!}-1,n)=p`, `p-1` smooth | `pollard-pm1*.md` |

## Exponent → the `ed≡1` leaks

| `wiener` | `d<n^0.25` → CF | `wiener*.md` |
| `boneh-durfee` | `d<n^0.292` → LLL | `boneh-durfee*.md` |
| `common-modulus` | `gcd(e1,e2)=1` → Bezout | `common-modulus*.md` |
| `factor-from-d` | `d`/`phi` held | `factor-from-d*.md` |

## Partial → the small-root bugs

| `coppersmith-*` | `p`/`m` bits → LLL | `coppersmith*.md` |

## Relation/leak → the structure bugs

| `franklin-reiter` | `m2=a·m1+b` → poly `gcd` | `franklin-reiter*.md` |
| `crt` | residues/Bellcore/dp | `crt*.md` |
| `rsa-decrypt` | `p`,`q`/`d` held | `rsa-decrypt*.md` |
| `eth-root` | `gcd(e,phi)>1` → `g` candidates | `eth-root*.md` |

## The verify

`pow(m,e,n)==c` / `p*q==n` — the mechanism-neutral gate.
