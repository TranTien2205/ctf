# Worked examples catalogue — the solves, indexed by shape

## The factor-recovery solves

| The attack | The chain | The file |
|---|---|---|
| `fermat` | `a²-n=b²` → `p,q` → `rsa-decrypt` | `worked-examples.md` ex1 |
| `batch-gcd` | `gcd(ni,nj)=p` → `rsa-decrypt` | `worked-examples.md` ex3 |
| `pollard-pm1` | `gcd(a^{B!}-1,n)=p` → `rsa-decrypt` | `worked-examples.md` ex6 |
| `coppersmith-*` | `p=a+x` → `factor-from-d` → `rsa-decrypt` | `worked-examples.md` ex7 |
| `crt` Bellcore | `gcd(s'^e-m,n)=q` → `factor-from-d` | `worked-examples-deep.md` |
| `factor-from-d` | `ed-1` → `p,q` → `rsa-decrypt` | `worked-examples.md` ex8 |

## The d-recovery solves

| The attack | The chain |
|---|---|
| `wiener` | CF `k/d` → `d` → `rsa-decrypt` |
| `boneh-durfee` | LLL `(k,s)` → `d`/`p,q` → `rsa-decrypt` |
| `crt` dp | `e·dp-1` → `p` → `factor-from-d` |

## The direct-m solves

| The attack | The chain |
|---|---|
| `small-e-root`/`nth-root` | `m=c^{1/e}` → `pow` verify |
| `hastad` | CRT → `m^e` → root → `pow` |
| `common-modulus` | Bezout → `m` → `pow` |
| `franklin-reiter` | poly `gcd` → `m` → `pow` |
| `crt` residues | CRT → `m` → `pow` |
| `eth-root` | the `g` candidates → `pow`+format |

## The verify

Every solve ends at `pow(m,e,n)==c` or `p*q==n`.

## The honest status

Catalogue — the examples are the published-standard shapes, not local solves.
